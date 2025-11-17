# TCP 三次握手和四次挥手

## TCP 三次握手（Three-Way Handshake）

TCP 建立连接的过程需要三次握手。

### 握手过程

```
客户端                              服务器
   |                                  |
   |  1. SYN (seq=x)                  |
   |--------------------------------->|
   |                                  |
   |  2. SYN-ACK (seq=y, ack=x+1)    |
   |<---------------------------------|
   |                                  |
   |  3. ACK (ack=y+1)               |
   |--------------------------------->|
   |                                  |
   |  【连接建立】                     |
```

### 详细步骤

#### 第一次握手 (SYN)
- **客户端** 发送 SYN 报文段
- 设置 `SYN=1`, `seq=x` (x 是随机初始序列号)
- 进入 `SYN_SENT` 状态
- 目的：告诉服务器客户端要建立连接

#### 第二次握手 (SYN-ACK)
- **服务器** 收到 SYN，发送 SYN-ACK 响应
- 设置 `SYN=1`, `ACK=1`, `seq=y`, `ack=x+1`
- 进入 `SYN_RCVD` 状态
- 目的：确认收到客户端的SYN，同时发送自己的SYN

#### 第三次握手 (ACK)
- **客户端** 收到 SYN-ACK，发送 ACK 确认
- 设置 `ACK=1`, `ack=y+1`
- 进入 `ESTABLISHED` 状态
- 服务器收到ACK后也进入 `ESTABLISHED` 状态
- 目的：确认收到服务器的SYN

### 为什么需要三次握手？

1. **防止旧的重复连接初始化**
   - 如果只有两次握手，旧的SYN包可能会导致错误的连接

2. **双方确认序列号**
   - 客户端和服务器都需要确认对方的初始序列号

3. **防止资源浪费**
   - 确保双方都准备好通信

## TCP 四次挥手（Four-Way Handshake）

TCP 断开连接需要四次挥手。

### 挥手过程

```
客户端                              服务器
   |                                  |
   |  1. FIN (seq=u)                  |
   |--------------------------------->|
   |                                  |
   |  2. ACK (ack=u+1)               |
   |<---------------------------------|
   |                                  |
   |  3. FIN (seq=v)                 |
   |<---------------------------------|
   |                                  |
   |  4. ACK (ack=v+1)               |
   |--------------------------------->|
   |                                  |
   |  【连接关闭】                     |
```

### 详细步骤

#### 第一次挥手 (FIN)
- **客户端** 发送 FIN 报文段
- 设置 `FIN=1`, `seq=u`
- 进入 `FIN_WAIT_1` 状态
- 表示客户端没有数据要发送了

#### 第二次挥手 (ACK)
- **服务器** 收到 FIN，发送 ACK
- 设置 `ACK=1`, `ack=u+1`
- 进入 `CLOSE_WAIT` 状态
- 客户端收到ACK后进入 `FIN_WAIT_2` 状态
- 此时服务器可能还有数据要发送

#### 第三次挥手 (FIN)
- **服务器** 发送完数据后，发送 FIN
- 设置 `FIN=1`, `seq=v`
- 进入 `LAST_ACK` 状态
- 表示服务器也没有数据要发送了

#### 第四次挥手 (ACK)
- **客户端** 收到 FIN，发送 ACK
- 设置 `ACK=1`, `ack=v+1`
- 进入 `TIME_WAIT` 状态
- 等待 2MSL 后关闭
- 服务器收到ACK后关闭连接

### TIME_WAIT 状态

客户端在最后一次ACK后会等待 2MSL (Maximum Segment Lifetime)：

- **目的1**: 确保最后的ACK能到达服务器
  - 如果ACK丢失，服务器会重发FIN
  - 客户端可以重发ACK

- **目的2**: 确保旧连接的报文段都消失
  - 防止旧连接的数据影响新连接

- **MSL**: 通常是 30秒 到 2分钟
- **2MSL**: 1-4 分钟

### 为什么需要四次挥手？

TCP 是**全双工**通信：
- 客户端的 FIN 只表示客户端不再发送数据
- 服务器可能还有数据要发送
- 所以需要两个方向各自独立关闭

## 状态转换图

### 客户端状态转换
```
CLOSED -> SYN_SENT -> ESTABLISHED -> FIN_WAIT_1 ->
FIN_WAIT_2 -> TIME_WAIT -> CLOSED
```

### 服务器状态转换
```
CLOSED -> LISTEN -> SYN_RCVD -> ESTABLISHED ->
CLOSE_WAIT -> LAST_ACK -> CLOSED
```

## 常见问题

### 1. SYN 洪水攻击
- 攻击者发送大量SYN包但不响应SYN-ACK
- 服务器维持大量半连接状态
- **防御**: SYN Cookie

### 2. TIME_WAIT 过多
- 大量短连接导致 TIME_WAIT 堆积
- **解决**:
  - 调整系统参数允许 TIME_WAIT 重用
  - 使用连接池
  - 使用长连接

### 3. 连接超时
- 网络延迟导致握手超时
- **配置**: 调整超时时间和重传次数

## TCP 报文段格式

```
0                   16                  31
+-------------------+-------------------+
|   Source Port     |  Destination Port |
+-------------------+-------------------+
|        Sequence Number               |
+--------------------------------------+
|     Acknowledgment Number            |
+------+-------+-----+-----------------+
| Data |       |Flags|  Window Size    |
|Offset|Reserve|     |                 |
+------+-------+-----+-----------------+
|   Checksum        |  Urgent Pointer  |
+-------------------+------------------+
|            Options (if any)          |
+--------------------------------------+
|              Data                    |
+--------------------------------------+
```

### 重要标志位
- **SYN**: 同步序列号，建立连接
- **ACK**: 确认号有效
- **FIN**: 发送方完成发送
- **RST**: 重置连接
- **PSH**: 推送数据
- **URG**: 紧急指针有效

## 实用命令

### 查看 TCP 连接状态
```bash
# Linux
netstat -an | grep tcp

# 查看 TIME_WAIT 数量
netstat -an | grep TIME_WAIT | wc -l

# 使用 ss 命令（更快）
ss -tan state time-wait | wc -l
```

### tcpdump 抓包
```bash
# 抓取三次握手
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0'

# 抓取四次挥手
tcpdump -i eth0 'tcp[tcpflags] & (tcp-fin) != 0'
```

## 编程示例

### Python Socket 三次握手
```python
import socket

# 创建 socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect() 会自动进行三次握手
sock.connect(('example.com', 80))

# 使用连接
sock.send(b'GET / HTTP/1.1\r\n\r\n')

# close() 会自动进行四次挥手
sock.close()
```

## 面试常见问题

**Q: 为什么建立连接是三次握手，关闭连接是四次挥手？**

A:
- 建立连接时，服务器的 SYN 和 ACK 可以合并发送（SYN-ACK）
- 关闭连接时，接收方的 ACK 和 FIN 通常不能合并
- 因为接收方收到 FIN 后可能还有数据要发送

**Q: TIME_WAIT 状态的作用？**

A:
1. 确保最后的 ACK 能被对方收到
2. 确保旧连接的报文段都在网络中消失

**Q: 如果第三次握手的 ACK 丢失会怎样？**

A:
- 服务器会重发 SYN-ACK（因为没收到ACK）
- 客户端收到后会再次发送 ACK
- 如果一直收不到，服务器会超时放弃
