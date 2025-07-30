# Hàm random của các ngôn ngữ

## 1. Mersenne Twister MT19937 (Python)
**Mersenne Twister (MT19937)** là một thuật toán tạo số giả ngẫu nhiên phổ biến được dùng trong ngôn ngữ Python sử dụng số nguyên tố Mersenne $2^{19937} - 1$ làm độ dài chu kì của nó. Bao gồm các hằng số:
- Độ rộng `w = 32` bit (tức là MT19937 sẽ chỉ sinh ra các số nguyên nằm trong khoảng $[0, 2^w - 1]$).
- Kích thước trạng thái `n = 624` phần tử 32-bit.
- Chỉ số trễ `m = 397`.
- Mask chia cao thấp gồm phần **upper** gồm 1 bit cao nhất (bit 31) và phần **lower** gồm 31 bit thấp.
- `a` là ma trận "twits" ở dạng bitmask.
- `(u, d), (s, b), (t, c), l` là các tham số **tempering** (dịch trái, dịch phải và AND với bitmask).
- `f` là hằng số khởi tạo.

Quy trình của MT19937 gồm 3 phần chính:

### Initialization (seeding)
Ban đầu khởi tạo `mt[0] = seed`.

Với $i = 1...n-1$:

$$
\text{mt}[i] = (f \cdot (\text{mt}[i-1] \oplus (\text{mt}[i-1] >> (w-2))) + i) \pmod {2^w}
$$

Đặt `index = n` để lần đầu rút sẽ kích hoạt `twist()` luôn.

Ý nghĩa: công thức này làm khuếch tán bit từ `mt[i - 1]` sang `mt[i]` và phân bổ thông tin của seen lên toàn trạng thái.

### Twist
Tạo ra 2 mask:
- `upper = 1 << (w - 1)` (bit thứ 31 bật, còn lại tắt).
- `lower = (1 << (w - 1)) - 1` (bit thứ 31 tắt, còn lại bật).

Với mỗi $i = 0...n-1$:
1. Ghép 1 bit cao của `mt[i]` và 31 bit thấp của `mt[(i+1) $ n]`:

$$
x = (\mathrm{mt}[i] \,\&\, \mathrm{upper}) \;\mid\; (\mathrm{mt}[(i+1)\bmod n] \,\&\, \mathrm{lower})
$$


2. Dịch phải 1 bit:

$$
xA = x >> 1
$$

3. Nếu $x$ lẻ, twist bằng ma trận $a$:

$$
(x \ \& \ 1) = 1 \Rightarrow xA = xA \oplus a
$$

4. Cập nhật phần tử mới:

$$
\text{mt}[i] = \text{mt}[(i+1)\bmod n] \oplus xA
$$

Ý nghĩa: từ `mt[0..n-1]` hiện tại, sinh ra 624 trạng thía mới cho lần rút tiếp theo. Mỗi trạng thái mới là XOR của một trạng thái "cách nhau $m$ đơn vị" và sử dụng $upper, lower$ sao đó XOR với $a$ làm cho trạng thái mới đảm bảo tính hỗn loạn.

### Tempering
Từ `mt[index]` tiếp tục đi qua các bước XOR + shift + mask với các tham số cố định:

```
x = self.mt[self.index]
x ^= x >> self.u
x ^= (x << self.s) & self.b
x ^= (x << self.t) & self.c
x ^= x >> self.l
```

Ý nghĩa: cải thiện phân bố bit trên đầu ra (đạt các tính chất cân bằng k-distribution).