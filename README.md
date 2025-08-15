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

### Thuật toán

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

### Thuật toán
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
Bộ sinh số ngẫu nhiên `random()` trong thư viện **glibc** sử dụng thuật toán **linear additive feedback** (phản hồi cộng tuyến tính), thường được gọi là **lagged Fibonacci generator**. Trên thực tế, quá trình sinh số sau khi khởi tạo hoàn toàn tuyến tính trong modulo $2^{32}$. Phần duy nhất có tính phi tuyến nhẹ là khâu khởi tạo (seeding), sử dụng bộ sinh MINSTD với modulo $2^{31} - 1$. Do đặc điểm tuyến tính này, `random()` trong **glibc** không phù hợp cho mục đích mật mã, nhưng lại hiệu quả và đủ tốt cho các ứng dụng giả lập, thống kê, ...

### Thuật toán
Các hằng số được sử dụng trong thuật toán:
- $2147483647 = 2^{31} - 1$
- $4294967296 = 2^{32}$

Với một giá trị `seed` được cho ban đầu, khởi tạo vector $r_0, r_1,...,r_{33}$ như sau:
- $r_0 = seed$
- $r_i = (16807 * r_{i-1}) \bmod 2147483647$ $(\text{for} \ i = 1...30)$
- $r_i = r_{i-31}$ $(\text{for} \ i = 31...33)$

Sau phần khởi tạo, dãy chính được sinh bằng vòng lặp **linear feedback**:
- $r_i = (r_{i-3} + r_{i-31}) \bmod 4294967296$  $(\text{for} \ i \ge 34)$

Kết quả của lần `random()` thứ $i$ sẽ là:
- $output_i = r_{i+344} >> 1$

Xem đầy đủ chi tiết tại [đây](https://www.mscs.dal.ca/~selinger/random/).

### Cracking
Dễ thấy, các điểm yếu có thể khai thác trong cách implement `random()` của glibc như sau:
- Công thức `state[i] = state[i - 3] + state[i - 31]` là tuyến tính và được áp dụng liên tục.
- `Output` chỉ bị mất 1 bit cuối, nên một giá trị `state[i]` chỉ có duy nhất 2 khả năng (lsb = 0 hoặc 1).
- Nếu ta biết **2 trong 3** giá trị `(state[i], state[i - 3], state[i - 31])`, ta hoàn toàn có thể tính được giá trị còn lại. (*)
- Với đủ các `output` liên tiếp $\Rightarrow$ có thể lan truyền để khôi phục lại toàn bộ mảng trạng thái.

Từ đó, thuật toán khôi phục `seed` như sau:
1. Từ `output` suy ngược lại một phần trạng thái
    - Nếu có đủ 3 giá trị liên quan (`output[i, i-3, i-31]`) và công thức không khớp, ta có thể đoán được bit thấp bị mất, rồi ghép lại thành trạng thái gốc (chưa dịch phải).
    - Làm như vậy cho toàn bộ dữ liệu thu được để có một mảng trạng thái, trong đó nhiều phần tử vẫn chưa biết (`None`).
2. Khôi phục giai đoạn khởi tạo (344 trạng thái).
    - Từ các trạng thái đã biết, chạy ngược công thức cộng để điền thêm các giá trị còn thiếu trong 344 trạng thái đầu tiên. (Theo nhận xét (*)).
3. Tìm một giá trị thuộc 31 trạng thái LCG gốc.
    - 31 trạng thái đầu tiên được tính bằng LCG, nên nếu tìm được một giá trị trong nhóm này, ta có thể tính ra toàn bộ các giá trị còn lại bằng công thức LCG.
    - Giả sử ta tìm được một giá trị có vị trị là `base_idx`, ta có thể khôi phục được các trạng thái trước và sau `base_idx` bằng cách sử dụng công thức:

$$
init_i = 16807^{i-baseidx} * init_{baseidx} \pmod {2147483647}
$$

4. Ghép tất cả và lan truyền để điền các giá trị thiếu.
    - Sau khi có được 31 giá trị đầu và một phần 344 trạng thái đầu, ghép tất cả vào một mảng trạng thái mới. Dùng lại công thức cộng để lan truyền, điền nốt các giá trị chưa biết.

## 4. Xorshift128 (JavaScript)
`Math.random()` là hàm sinh số ngẫu nhiên trả về một số thực dương, lớn hơn hoặc bằng $0$ nhưng nhỏ hơn $1$, được chọn ngẫu nhiên hoặc bán ngẫu nhiên với phân phối gần như đồng đều trong phạm vi đó, sử dụng thuật toán hoặc chiến lược phụ thuộc vào việc implement. Trong engine `V8`, `Math.random()` hiện tại được triển khai dựa trên thuật toán **xorshift128**.

### Thuật toán

Trong V8, `Math.random()` sẽ dùng PRNG `xorshift128` để sinh ra **64 số nguyên 64-bit** một lúc. Sau đó lưu vào bộ nhớ đệm `cache` 64 phần tử. Mỗi lần gọi hàm `random()` thì lấy 1 phần tử trong `cache`, chuyển thành double rồi trả về kết quả đó. Khi `cache` hết giá trị, chạy lại `xorshift128` để refill lại 64 giá trị mới.

Chi tiết hơn:

PRNG `xorshift128` lưu trạng thái 128-bit trong 2 biến 64-bit: `state0, state1`. Mỗi lần cập nhật, công thức của nó như sau:
```python
def xs128(state0, state1):
    mask = (1 << 64) - 1
    s1 = state0 & mask
    s0 = state1 & mask
    s1 ^= (s1 << 23) & mask
    s1 ^= (s1 >> 17) & mask
    s1 ^= s0
    s1 ^= (s0 >> 26) & mask
    return s0, s1
```

`V8` không gọi PRNG mỗi lần mà:
- Khi bộ nhớ đệm `cache` trống $\Rightarrow$ chạy PRNG 64 lần $\Rightarrow$ nạp 64 số nguyên vào `cache[0..63]`.
- `cache_idx` bắt đầu vị trí $63$ (cuối mảng).
- Mỗi lần gọi `Math.random()`:
  - Lấy `cache[cache_idx]`, giảm `cache_idx` đi 1 đơn vị.
  - Nếu `cache_idx < 0` thì refill lại `cache`.

Các số nguyên 64-bit từ `xorshift128` sẽ được chuyển đổi thành số thực `[0, 1)` bằng cách:
1. Bỏ đi 12 bit thấp nhất:
    - Trong IEEE754 double-precision (64-bit), phần mantissa chỉ có 52 bit.
    - `V8` không dùng toàn bộ 52 bit mà bỏ hẳn 12 bit thấp nhất của số nguyên để tránh các vấn đề về tính ngẫu nhiên ở các bit cuối của `xorshift128+`.
2. Chèn bit mũ để tạo số trong `[1, 2)`.
    - Một số double có dạng: `sign (1 bit) | exponent (11 bit) | mantissa (52 bit)`.
    - `V8` đặt `exponent = 0x3FF` để biểu diễn số `1.xxxxx...` trong chuẩn IEEE754. Phần mantissa được lấp đầy bởi 52 bit được giữ lại của `state0`.
3. Chuyển bit sang double
    - Sau khi gộp các bit `exponent` và `mantissa` vào một giá trị 64-bit, `V8` ép kiểu nó sang `double`. Kết quả thu được nằm trong khoảng `[1, 2)`, ta trừ nó đi $1$ đơn vị để đưa nó về đúng phạm vi kết quả của `Math.random()`.

### Cracking
`xorshift128` là một hàm chỉ gồm các phép `XOR` và `Shift`, chúng đều tuyến tính trên `GF(2)` với trạng thái 64-bit. Tức là, mỗi bit của output sau một số bước sẽ là tổ hợp tuyến tính của các bit ban đầu.

Vậy nên, nếu thu thập đủ số lượng output `double` liên tiếp, ta có nhiều phương trình tuyến tính trên 64 biến (các bit của trạng thái ban đầu). Giải hệ phương trình này trên `GF(2)` sẽ tìm được trạng thái ban đầu.

Chi tiết thuật toán:
1. Khôi phục lại 52 bit MSB của các `state0`
```python
def v8_from_double(double):
    """
    Convert a double back to a 64-bit integer.
    The 12 least significant bits of the result cannot be recovered.
    """
    if double == 1.0:
        return 0xffffffffffffffff
    return (struct.unpack('<Q', struct.pack('d', double + 1.0))[0] & 0xfffffffffffff)
```

