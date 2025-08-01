# Crack random function of some languages.

## 1. Mersenne Twister MT19937 (Python)
**Mersenne Twister (MT19937)** là một thuật toán tạo số giả ngẫu nhiên phổ biến được dùng trong ngôn ngữ Python sử dụng số nguyên tố Mersenne $2^{19937} - 1$ làm độ dài chu kì của nó. Bao gồm các hằng số:
- Độ rộng `w = 32` bit (tức là MT19937 sẽ chỉ sinh ra các số nguyên nằm trong khoảng $[0, 2^w - 1]$).
- Kích thước trạng thái `n = 624` phần tử 32-bit.
- Chỉ số trễ `m = 397`.
- Mask chia cao thấp gồm phần **upper** gồm 1 bit cao nhất (bit 31) và phần **lower** gồm 31 bit thấp.
- `a = 0x9908b0df` là ma trận "twits" ở dạng bitmask.
- `(u, d), (s, b), (t, c), l` là các tham số **tempering** (dịch trái, dịch phải và AND với bitmask).
- `f = 0x6C078965` là hằng số khởi tạo.

Quy trình của MT19937 gồm 3 phần chính:

### Thuật toán:

#### Initialization (seeding)
Ban đầu khởi tạo `mt[0] = seed`.

Với $i = 1...n-1$:

$$
\text{mt}[i] = (f \cdot (\text{mt}[i-1] \oplus (\text{mt}[i-1] >> (w-2))) + i) \pmod {2^w}
$$

Đặt `index = n` để lần đầu rút sẽ kích hoạt `twist()` luôn.

**Ý nghĩa:** công thức này làm khuếch tán bit từ `mt[i - 1]` sang `mt[i]` và phân bổ thông tin của seen lên toàn trạng thái.

#### Twist
Tạo ra 2 mask:
- `upper = 1 << (w - 1)` (bit thứ 31 bật, còn lại tắt).
- `lower = (1 << (w - 1)) - 1` (bit thứ 31 tắt, còn lại bật).

Với mỗi $i = 0...n-1$:
1. Ghép 1 bit cao của `mt[i]` và 31 bit thấp của `mt[(i+1) $ n]`:

$$
x = (\text{mt}[i] \ \land \ \text{upper}) \ \big| \ (\text{mt}[(i+1)\bmod n] \ \land \ \text{lower})
$$

2. Dịch phải 1 bit:

$$
xA = x >> 1
$$

3. Nếu $x$ lẻ, twist bằng hằng số $a$:

$$
(x \ \land \ 1) = 1 \Rightarrow xA = xA \oplus a
$$

4. Cập nhật phần tử mới:

$$
\text{mt}[i] = \text{mt}[(i+1)\bmod n] \oplus xA
$$

**Ý nghĩa:** từ `mt[0..n-1]` hiện tại, sinh ra 624 trạng thía mới cho lần rút tiếp theo. Mỗi trạng thái mới là XOR của một trạng thái "cách nhau $m$ đơn vị" và sử dụng `upper, lower` sao đó XOR với $a$ làm cho trạng thái mới đảm bảo tính hỗn loạn.

#### Tempering
Từ `mt[index]` tiếp tục đi qua các bước (XOR + shift + mask) với các tham số cố định:

```
x = self.mt[self.index]
x ^= x >> self.u
x ^= (x << self.s) & self.b
x ^= (x << self.t) & self.c
x ^= x >> self.l
x &= self.d
```

**Ý nghĩa:** cải thiện phân bố bit trên đầu ra (đạt các tính chất cân bằng k-distribution).

### Cracking
Thuật toán như sau: nhận **ít nhất 624** giá trị 32-bit đã **tempered** do MT19937 sinh ra, viết hàm **untemper** để lấy lại 624 phần tử trạng thái `mt[0...623]`, rồi dựng lại **state tuple** đúng format của `random.Random` để từ đó ta tiếp tục sinh đúng chuỗi.

Vì MT19937 có kích thước trạng thái `n = 624` 32-bit, nên khi biết đủ 624 đầu ra (và thứ tự của chúng) thì ta hoàn toàn có thể khôi phục toàn bộ trạng thái.

Ta đã biết, `tempering` là một hàm **song ánh**, nó chỉ đơn giản là XOR với các bản dịch bit của chính nó. Vì vậy, nếu biết đầu ra, ta có thể khôi phục lại trạng thái gốc bằng cách `untemper` theo thứ tự ngược lại.

```python
def unshiftRight(self, x, shift):
    res = x
    for i in range(32):
        res = x ^ res >> shift
    return res

def unshiftLeft(self, x, shift, mask):
    res = x
    for i in range(32):
    res = x ^ (res << shift & mask)
    return res

def untemper(self, v):
    """ Reverses the tempering which is applied to outputs of MT19937 """

    v = self.unshiftRight(v, self.l)
    v = self.unshiftLeft(v, self.t, self.c)
    v = self.unshiftLeft(v, self.s, self.b)
    v = self.unshiftRight(v, self.u)
    return v
```

- Với phép **dịch phải shift**, bit ở vị trí `i` của `res` phụ thuộc vào bit `i` của `x` và bit `i+k` của `res` (đã biết khi ta giải từ MSB -> LSB). Lặp lại ~32 lần để đảm bảo các bit phụ thuộc lan truyền hết đến các LSB. (thực tế ta chỉ cần ceil(32/shift) lần lặp, nhưng để 32 luôn cho tổng quát).
- Với phép **dịch trái shift**, tương tự nhưng ta giải ngược từ LSB -> MSB và có thêm `mask` để triệt tiêu các bit không ảnh hưởng.

Sau khi khôi phục lại được `mt[0..623]` rồi, phần còn lại là tìm `index` và dựng lại state đúng định dạng của `random.Random` để tiếp tục sinh ra đúng chuỗi. Ta đã biết, MT19937 dùng con trỏ `index` chỉ vào phần tử kết tiếp sẽ được xuất ra (sau `tempering`). `index` $\in$ [0, 1, 2,...,624], `index = 624` có nghĩa là đã dùng hết 624 giá trị trong trạng thái hiện tại, lần rút kế tiếp sẽ thực hiện **twist** và gán `index = 0`.

Có 2 trường hợp xảy ra:
- **Có ít nhất 625 đầu ra liên tiếp:** ta sẽ brute-force `index` bằng cách thử tất cả các khả năng [1 ... 625] rồi kiểm tra đầu ra kế tiếp có khớp với `ouputs[624]` không.
- **Chỉ có đúng 624 đầu ra:** ta giả sử 624 đầu ra liên tiếp đó bắt đầu ngay sau một lần **twist**, khi đó `index = 624`. Ngược lại, chuỗi sau đó sẽ bị lệch.

Sau khi tìm được `index` rồi thì ta xây dựng state tuple `(3, tuple(ivals + [index]), None)` và `setstate` cho hàm `random.Random`.


## 2. Lehmer random number generator (Bash)
**Lehmer random number generator** hay còn được gọi là **Park-Miller random number generator** là một loại **linear congruential generator (LCG)** hoạt động trong nhóm nhân các số nguyên modulo $N$. Có công thức là:

$$
X_{k+1} = a \cdot X_k \mod m
$$

Trong đó modulo $m$ là một số nguyên tố hoặc là lũy thừa của một số nguyên tố, hệ số nhân $a$ là một phần tử có bậc là $m$ và $seed = X_0$ nguyên tố cùng nhau với $m$. Tham khảo thêm ở [đây](https://en.wikipedia.org/wiki/Lehmer_random_number_generator)

Hàm `$RANDOM` của Bash sử dụng Park-Miller LCG để sinh ra dãy số ngẫu nhiên. Sau mỗi bước, cập nhật `seed` bằng công thức LCG, kết quả của `$RANDOM` là **15 bit cuối** của `seed` (Bash 5.0) hoặc là một biến thể XOR (Bash >= 5.1).

### Thuật toán:
Nhận đầu vào là một giá trị `seed`, nếu như `seed = 0` thì gán `seed = 123459876`.

```python
def next_seed(self) -> int:
    if self.seed == 0:
        self.seed = 123459876

    self.seed = (self.seed * self.a) % self.m
    return self.seed
```

Áp dụng công thức Park-Miller LCG để sinh ra `seed` mới.

Sau khi có `seed` rồi, hàm random sẽ trả về:
- `result = self.seed & 0x7fff`: chỉ lấy 15 bit thấp nhất của `seed`.
- `result = ((self.seed >> 16) ^ (self.seed & 0xffff)) & 0x7fff`: XOR 15 bit cao với 16 bit thấp, sau đó lấy 15 bit thấp nhất.

### Cracking
Đặc diểm của hàm LCG là ta không có công thực trực tiếp để từ `output` tìm lại được `seed`. Do đó kỹ thuật crack của hàm `$RANDOM` sẽ là thử từng khả năng của `seed`, mô phỏng lại quá trình `BashRandom`, rồi so sánh kết quả với chuỗi `output` đã biết. Nếu khớp hoàn toàn thì đó là `seed` mà ta cần tìm.

Vì `seed` có độ lớn là **32-bit**, nếu brute-force bình thường thì rất lâu mới chạy ra nên ta sử dụng bộ **xử lí song song (multiprocessing)** của Python để chia nhỏ quá trình tính toán ra. `seed` được duyệt theo các `chunk` giúp tối ưu hóa bộ nhớ và giảm độ trễ trong xử lý.

Cách thực hiện cụ thể như sau:
- Chia toàn bộ không gian `seed` thành nhiều đoạn nhỏ.
- Mỗi đoạn sẽ được giao một tiến trình xử lí riêng (song song).
- Trong mỗi tiến trình:
  - Duyệt qua từng `seed` trong đoạn.
  - Khởi tạo `BashRandom` với `seed` hiện tại.
  - Sinh ra các số liên tiếp từ hàm `next_16()` và so sánh với chuỗi `output`.
  - Nếu khớp thì dừng lại và trả về `seed`.

Đối với **cracker** dùng 2 hoặc 1 số đầu ra:
- Làm tương tự duyệt toàn bộ không gian `seed`, nhưng thay vì tìm chính xác 1 `seed` đúng, ta sẽ gửi tất cả các `seed` phù hợp vào `queue`.
- Điều này giúp ta có thể tìm ra nhiều `seed` có thể tạo cùng một chuỗi đầu ra (do hàm random không phải luôn là 1-1).

## 3. GLIBC random number generator (C)
Bộ sinh số ngẫu nhiên `random()` trong thư viện **glibc** sử dụng thuật toán **linear additive feedback** (phản hồi cộng tuyến tính), thường được gọi là **lagged Fibonacci generator**. Trên thực tế, quá trình sinh số sau khi khởi tạo hoàn toàn tuyến tính trong modulo $2^{32}$. Phần duy nhất có tính phi tuyến nhẹ là khâu khởi tạo (seeding), sử dụng bộ sinh MINSTD với modulo $2^{32} - 1$. Do đặc điểm tuyến tính này, `random()` trong **glibc** không phù hợp cho mục đích mật mã, nhưng lại hiệu quả và đủ tốt cho các ứng dụng giả lập, thống kê, ...

### Thuật toán:
