from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, execute
from qiskit.providers.aer import AerSimulator
from qiskit.visualization import plot_histogram
import numpy as np
from fractions import Fraction

def iqft(n):
    br = QuantumRegister(n, 'b')
    qc = QuantumCircuit(br)
    for sbit in range(n // 2):
        qc.swap(sbit, n - sbit - 1)
    for hbit in range(0, n, 1):
        for cbit in range(hbit - 1, -1, -1):
            qc.cp(-np.pi / 2**(hbit - cbit), cbit, hbit)
        qc.h(hbit)
    return qc

def qc_mod15(a, power,show=False):
    assert a in [2, 4, 7, 8, 11, 13], "Invalid value of argument a: " + str(a)
    qrt = QuantumRegister(4, 'target')
    U = QuantumCircuit(qrt)
    for i in range(power):
        if a in [2, 13]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [7, 8]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a in [4, 11]:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7, 11, 13]:
            for j in range(4):
                U.x(j)
    U = U.to_gate()
    U.name = f'{a}^{power} mod 15'
    C_U = U.control()
    return C_U

def qpf15(count_no,a):
    qrc = QuantumRegister(count_no,'count')
    qry = QuantumRegister(4,'y')
    clr = ClassicalRegister(count_no,'c')
    qc = QuantumCircuit(qrc,qry,clr)
    for cbit in range(count_no):
        qc.h(cbit)
    qc.x(qry[0])
    for cbit in range(count_no):
        qc.append(qc_mod15(a,2**cbit),[cbit] + list(range(count_no,count_no+4)))
    qc.append(iqft(count_no).to_gate(label = 'IQFT'),range(count_no))
    qc.measure(range(count_no),range(count_no))
    return qc

sim = AerSimulator()

n = int(input())

for _ in range(n):
    c, a = map(int, input().split())
    
    cir = qpf15(c,a)
    job = execute(cir,backend = sim ,shots =1000)
    result = job.result()
    counts = result.get_counts(cir)
    for counting_bits in sorted(counts.keys(), key=lambda x: int(x, 2)):
        dec = int(counting_bits, base=2)
        phase = dec / (2**c)
        frac = Fraction(phase).limit_denominator(15)
        period = frac.denominator
        print('%s %d' % (counting_bits, period))
