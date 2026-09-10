# Course: Microprocessor & Microcontroller
Domain: Customized Lesson Plan
Sub-Domain: Microprocessor & Microcontroller
Course ID: 229

## Module: 8086 Architecture, Memory Segmentation & Peripheral Interfacing
Source: MPMC Department Course Curriculum — Units 1, 3 & 4
Section: Hardware Architecture & 8255 PPI Interfacing

### 1. 8086 Microprocessor Architecture
The 8086 is a 16-bit microprocessor with a 20-bit address bus, enabling it to directly address up to $2^{20} = 1\text{ MB}$ of physical memory.
The internal architecture is partitioned into two functional units operating concurrently (pipelining):
1. **Bus Interface Unit (BIU)**:
   - Fetches instructions from memory and places them in a 6-byte Instruction Queue.
   - Calculates 20-bit physical addresses using Segment Registers (`CS`, `DS`, `SS`, `ES`) and the Instruction Pointer (`IP`).
   - Handles all read and write bus cycles to memory and I/O ports.
2. **Execution Unit (EU)**:
   - Decodes and executes instructions fetched from the queue.
   - Contains the 16-bit Arithmetic Logic Unit (ALU), Flags register, General Purpose Registers (`AX`, `BX`, `CX`, `DX`), and Pointer/Index Registers (`SP`, `BP`, `SI`, `DI`).

### 2. Memory Segmentation in 8086
Physical memory is divided into segments of up to 64 KB each:
- **Code Segment (CS)**: Holds executable machine instructions.
- **Data Segment (DS)**: Holds program data and variables.
- **Stack Segment (SS)**: Stores return addresses and local stack frames.
- **Extra Segment (ES)**: Used for string and destination data operations.
- **Physical Address Calculation**:
  $$\text{Physical Address} = (\text{Segment Register} \times 16) + \text{Offset Register} = (\text{Segment} \ll 4) + \text{Offset}$$

### 3. Interfacing of 8086 with Peripheral Devices
Interfacing connects external I/O hardware to the CPU bus.
- **8255 Programmable Peripheral Interface (PPI)**:
  - Contains 24 programmable I/O pins organized into three 8-bit ports: Port A, Port B, and Port C (split into Port C Upper and Port C Lower).
  - **Operating Modes**:
    - **Mode 0 (Basic I/O)**: Simple input or output with no handshaking.
    - **Mode 1 (Strobed I/O)**: Unidirectional transfer using handshaking control signals via Port C pins.
    - **Mode 2 (Strobed Bidirectional I/O)**: Port A becomes a bidirectional bus using 5 handshake pins of Port C.
    - **BSR (Bit Set/Reset) Mode**: Permits individual setting or clearing of any of the 8 bits of Port C without affecting other pins.

### 4. 8051 Microcontroller Architecture
- 8-bit microcontroller with Harvard architecture (separate program and data memory spaces).
- 4 KB on-chip ROM, 128 bytes on-chip RAM, four 8-bit parallel I/O ports (P0, P1, P2, P3).
- Two 16-bit Timers/Counters (Timer 0 and Timer 1), full-duplex UART serial port, and 5 interrupt sources (two external interrupts, two timer interrupts, one serial port interrupt).
