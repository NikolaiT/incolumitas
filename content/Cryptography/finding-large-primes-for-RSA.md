Title: How to find large prime numbers for RSA with the Miller-Rabin Primality Test
Date: 2018-08-12 19:05
Modified: 2018-08-13 21:50
Author: Nikolai Tschacher
Category: Security, Cryptography
Tags: Python, Primes, Math, RSA, asymmetric key cryptography, Miller-Rabin Primality Test, Fermat
Slug: finding-large-prime-numbers-and-rsa-miller-rabin-test
Status: published

## Introduction

All sources for this blog post can be found in the [Github repository about large primes](https://github.com/NikolaiT/Large-Primes-for-RSA). The most recent version of the sources may only be found in the Github repository.

It has been a long time since I found the energy to write a new blog post. In this article, I am going to dig into a interesting area of cryptography: The task to **find large prime numbers**. We hopefully are all familiar with the concept of prime numbers. Prime numbers are integers $p$ which are dividable only by $p$ itself and $1$. But why is it necessary to find large prime numbers in the area of cryptography?

One of the first asymmetric cryptosystems invented was RSA (1977). As all public key algorithms, the security of RSA depends on the existence of a one-way function.

In the case of RSA, the one-way function is built on top of the integer factorization problem: Given two prime numbers $p,q\in \mathbb{N}$, it is straightforward to calculate $n=p \cdot q$, but it is computationally infeasible to reverse this multiplication by finding the factors $p$ and $q$ given the product $n$. Even when the primes $p$ and $q$ are very large integers (say with lengths of $2^{1024}$), multiplication is computationally efficient. Prime factorization however is a [computationally hard problem](https://en.wikipedia.org/wiki/Integer_factorization). This one-way property is exploited in  the asymmetric cryptostystem RSA.

In the following sections we introduce the necessary RSA cryptosystem theory and the required algorithms to implement RSA in a simple Python program. Please never use the resulting code in production, because I am most likely introducing some mistakes that comprise the security of the cryptosystem.

## RSA

RSA is a public key crypytosystem that can be used for confidentiality, accountability and digitial signatures. Therefore every participant creates a public and a private key. In RSA, the private key is denoted as $K_{private}=(d)$ and the public key is $K_{public}=(e,n)$. All operations within RSA are conducted in the ring $\mathbb{Z_{n}}=\{0,1,...,n-1\}$ and the numbers $n,d,e$ are usually very large integers with bitlengths larger then 512.

### Encryption

To encrypt the plaintext $x \in \mathbb{Z_{n}}$, the function

$$y=e_{K_{public}}(x) \equiv x^e \pmod n$$

is calculated, whereby the ciphertext $y$ again is a element of $\mathbb{Z_{n}}$.

### Decryption

To decrypt the ciphertext $y$, the private key $K_{private}=(d)$ is needed:

$$x = d_{K_{private}}(y) \equiv y^d \pmod n$$

Encryption and Decryption is essentially modular exponentiation within the ring $\mathbb{Z_{n}}$. This means that we need to perform a very large exponentiation with exponents with bitlengths of $1024$ and more. It turns out that there is a fast algorithm to perform this computation: **The square-and-multiply algorithm.**

This straightforward approach leaves us however with several requirements:

+ It must be computationally infeasible to determine the private key $d$ from the public key $(e,n)$.
+ The amount of data that can be encrypted can be maximally $n$. When we chose $n=2^{1024}$, we may encrypt $1024$ bits at once. Keep in mind that asymmetric cryptography is not intended for encryption of large datasets anyways. The usual approach is to exchange a symmetric session key with public key cryptography and then to continue working with symmetric block ciphers like AES. Therefore, the limited amount of data that can be encrypted at once does not pose a practical limitation.

### Key Generation for RSA

Key generation for the public key $K_{public}=(e,n)$ and the private key $K_{private}=(d)$ is done by the following algorithm:

1. Find two large primes $p$ and $q$ with bit-lengths of at least $1024$ bit
2. Calculate $p=n \cdot q$
3. Compute Euler's totient function $$\phi(n) = (q-1) \cdot (p-1)$$
4. Choose a public exponent $e \in \{1,2,...,\phi(n)-1\}$ such that $$gcd(e, \phi(n)) = 1$$
5. Find the private key $K_{private}=(d)$ such that $$d \cdot e \equiv \pmod{\phi(n)}$$

Finding keys $d$ and $e$ is done by randomly picking a public key $e \in \{0,1,...,\phi(n)-1\}$ and check whether $e$ satisfies $gcd(e, \phi(n)) = 1$. If this isn't the case, you can simply pick another public key $e$. We then apply the Extended Euclidean Algorithm (EEA) with the parameters $n$ and $e$ and obtain the equation

$$gcd(\phi(n), e) = s \cdot \phi(n) + t \cdot e$$

The parameter $t$ computed by the EEA is the the inverse of $e$ and therefore $d = t \pmod{\phi(n)}$. The parameter $s$ can be ignored for the purpose of RSA.

#### Extended Euclidean Algorithm (EEA)
As mentioned before, we need to compute $gcd(\phi(n), e)$ after we have chosen the public key exponent $e \in \{1,2,...,\phi(n)-1\}$ to obtain the form:
$$gcd(\phi(n), e) = s \cdot \phi(n) + t \cdot e$$ where $s$ and $t$ are integer coefficients. This can be done by computing the standard Euclidean Algorithm and simultaneously calculating the current remainder $r_i$ as $r_i = s_i \cdot r_0 + t_i \cdot r_1$.
The EEA algorithm is implemented below in Python. This implementation is not very efficient and not pretty at all, but it is sufficient for our purposes.
```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

def EEA(a, b):
    """
    Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    Extended Euclidean Algorithm (EEA)
    Parameters: Positive integers a and b whereby a > b
    Returns: ( gcd(a,b), s, t )  such that gcd(a,b) = s*a + t*b
    """
    assert a > b, 'a must be larger than b'
    x0, x1, y0, y1 = 1, 0, 0, 1
    while a != 0:
        q, b, a = b // a, a, b % a
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return  b, y0, x0

if __name__ == '__main__':
    print ( egcd( 30, 5) )
    print ( egcd( 17, 5) )
    print ( egcd( 234232, 774) )
```

#### Square and Multiply Algorithm

As we have seen in the RSA encryption and decryption function, we need to calculate huge exponents with bitlengths of at least $1024$. This computation is done efficiently with the square and multiply algorithm illustrated below. When an optional modulus $p$ is supplied, the modulus exponentiation is computed. The square and multiply algorithm is equivalent to the Python one-liner `pow(x, k, p)`

```Python
def square_and_multiply(x, k, p=None):
    """
    Square and Multiply Algorithm
    Parameters: positive integer x and integer exponent k,
                optional modulus p
    Returns: x**k or x**k mod p when p is given
    """
    b = bin(k).lstrip('0b')
    r = 1
    for i in b:
        r = r**2
        if i == '1':
            r = r * x
        if p:
            r %= p
    return r
```

### Practical Key Generation for RSA

Now that we have established the necessary theory and algorithms for the key generation, we can implement the second part of the key generation algorithm. The first part, **how to find large primes**, will be left over as the main contribution of this article. For now, lets just assume that we already have a method to create large prime numbers $p$ and $q$.

Therefore, we need to perform the steps 2. to 5. in the key generation process.

2. $p=n \cdot q$
3. Compute $\phi(n) = (q-1) \cdot (p-1)$
4. Choose a public exponent $e \in \{1,2,...,\phi(n)-1\}$ such that $$gcd(e, \phi(n)) = 1$$
5. Find the private key $K_{private}=(d)$ such that $$d \cdot e \equiv \pmod{\phi(n)}$$

I implemented those steps in the Python code below. Please don't use this code since it is intentionally erroneous.
```Python
import numpy as np
import math
import eea

def RSA_keygen(p, q):
    """
    Perform steps 2. to 5. in the RSA Key Generation process.
    """
    # step 2
    n = p * q
    # step 3
    phi_n = (p - 1) * (q - 1)
    # step 4 and step 5
    while True:
        e = np.random.randint(1, phi_n-1)
        if math.gcd(e, phi_n) == 1:
            # step 5
            gcd, s, t = eea.EEA(phi_n, e)
            if gcd == (s*phi_n + t*e):
                d = t % phi_n
                break
    return (e, n, d)

if __name__ == '__main__':
    print(RSA_keygen(53, 179))
```

## Generating large prime numbers $p$ and $q$ for RSA

Now that we completed all steps in the RSA key generation algorithm, we arrive at the last hurdle: How to find large prime numbers? The reader might suspect that the problem of determining whether a integer is a prime number is equally hard to the problem of factorization of a product of two primes. Of course, if we knew the factorization of a number, we could say whether this number is a prime or not. But do we need to factorize the numbers $p$ and $q$ in order to make a statement about their primality? Luckily, the answer is no. Primality tests exist that are computationally much more efficient then the integer factorization algorithms. There are two different primality tests that can be used to make a assertion whether a number is a prime.

One is called **Fermat Primality Test** and the other is known as the **Miller-Rabin Primality Test**. Both tests work with probabilities. They either output **"the number is a composite"** or **"the number is a prime"**. While the first statement is always true, the second statement is only true with a certain probability. Therefore those algorithms are probabilistic algorithms, so called **Monte Carlo Algorithms**. They output a primality statement with configurable probability.

For using RSA, we should chose the prime numbers $p$ and $q$ to have equal bit-lengths. So if we want RSA to run with a $n$ of 1024 bits, $p$ and $q$ should have a length of roughly $2^{512}$. But how can we be certain that there even exist prime numbers in those high ranges?

The [prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem) states that the probability that a random integer $k$ is prime is $P(k\text{ is a prime}) \approx \frac{1}{ln(k)}$. This follows from the main statement of the theorem, that prime numbers are asymptotically distributed among postive integers. This essentially means that the likelihood of a number being prime decreases slowly, the bigger the numbers get. The prime counting function $\pi(x)$ gives the number of primes less or equal to the real number $x$. The theorem states that the prime counting function is approximately $$\pi(x) \approx \frac{x}{ln(x)}$$

So the probability that a random integer with bitlength 512 is a prime is roughly $$P(2^{512} \text{ is prime}) \approx \frac{2}{ln(2^{512})} \approx \frac{2}{512 \cdot ln(2)} \approx \frac{1}{177}$$
which is a sufficiently high probability to **just randomly try out some odd numbers** and check them with the before-mentioned primality tests. Of course this process of randomly generating integer candidates shouldn't follow any deterministic logic. Otherwise an attacker could just replay the number generating process to find the primes that were used with RSA.

### Fermat Primality Test

We will not use the Fermat Primality Test, because it is not used in practice. We however quickly explain how this test works. This test is based on **Fermats Little Theorem**, which states that for any integer $a$ and prime number $p$ the following congruence holds: $$a^{p-1} \equiv 1 \pmod p$$

The Fermant Primality Test implemented in Python looks like this:
```Python
def fermat_primality_test(p, s=5):
    """
    a^(p-1) ≡ 1 mod p
    Input: prime candidate p and security paramter s
    Output: either p is a composite (always trues), or
            p is a prime (with probability)
    """
    if p == 2:
        return True
    if not p & 1: # if p is even, number cant be a prime
        return False

    for i in range(s):
        a = random.randrange(2, p-2)
        x = pow(a, p-1, p) # a**(p-1) % p
        if x != 1:
            return False
    return True
```

We will not use the Fermat Primality Test, since the test recognizes so called [Carmichael Numbers](https://en.wikipedia.org/wiki/Carmichael_number) as false positives. The test detects them as primes, even though they are pseudo primes (composites). Those numbers satisfy Fermats Little theorem above even though they are composite. For this reason, we are going to use a better Primality test, **the Miller-Rabin Test**.

### Miller-Rabin Primality Test

The Miller-Rabin Primality Test does not suffer from the limitations of the Fermat Primality Test. The test is based on the following mathematical observations. Every odd prime candidate $\hat p$ can be decomposed into the form $$\hat p - 1 = 2^u \cdot r$$ where $r$ is an odd integer. Lets say $\hat p = 12162881$, then we can write $\hat p-1$ in binary form $$bin(\hat p-1)_2 = 101110011001011101000000$$ The six zeroes on the right of the binary representation is the $2^u$ part and the rest $101110011001011101_2 = 190045$ is the odd $r$ part. So, $$\hat p-1 = 2^6 \cdot 190045 = 12162880$$

We learn that we can write any integer odd integer in the form $\hat p - 1 = 2^u \cdot r$. Now if we can find an integer $a$ such that $$a^r \not\equiv 1 \text{ mod } \hat p$$ and $$a^{r2^{k}} \not\equiv \hat p-1 \text{ mod } \hat p$$ for all $k \in \{0,1,...,u-1\}$, then $\hat p$ is composite. Otherwise it is likely a prime number. This is the Miller-Rabin Primality test.

The program below implements the Miller-Rabin Primality test. The function runs with acceptable speed and manages to find prime numbers with bitlengths of 2048 and above. I tested the primes on wolfram alpha to make sure that the generated numbers are in fact prime numbers. It took me 11 seconds to create a prime number with bitlength 2048 on my laptop, which is an acceptable bitlength in RSA practice. The random number generator however is not cryptographically secure and your probably should not make use of this prime number generator in your crypto library.

```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random
import math

"""
Generate prime numbers with the Miller-Rabin Primality Test.
For example useful for RSA prime number generation.

Generating a 2048 Bit Prime takes 11 seconds on my laptop:

    $ time python generate_primes.py
    18687035979164759960466760296206931684048670365627731168581812017856988830965115380270770738787389085718116283127416689537626499398221423941864131345832239438016468120676003896789194409913408615320990238865137075670115908902303929614757662667625835901714318363069492532318855874659498625458479795852690370922508203783115512849318748971370018698508809310655527728638519173556845950918379394995191185954569447143685450657088230510827375976211180471624026433253567874110992844598001397299587423215893037362024063057346321319865682948169846512354337641419160496824946523484362125933347273900485920490790844892064041256141 is prime with bitlength=2048

    real	0m11.099s
    user	0m11.068s
    sys	0m0.020s
"""

def fermat_primality_test(p, s=5):
    """
    a^(p-1) ≡ 1 mod p
    Input: prime candidate p and security paramter s
    Output: either p is a composite (always trues), or
            p is a prime (with probability)
    """
    if p == 2:
        return True
    if not p & 1: # if p is even, number cant be a prime
        return False

    for i in range(s):
        a = random.randrange(2, p-2)
        x = pow(a, p-1, p) # a**(p-1) % p
        if x != 1:
            return False
    return True

def square_and_multiply(x, k, p=None):
    """
    Square and Multiply Algorithm
    Parameters: positive integer x and integer exponent k,
                optional modulus p
    Returns: x**k or x**k mod p when p is given
    """
    b = bin(k).lstrip('0b')
    r = 1
    for i in b:
        r = r**2
        if i == '1':
            r = r * x
        if p:
            r %= p
    return r

def miller_rabin_primality_test(p, s=5):
    if p == 2: # 2 is the only prime that is even
        return True
    if not (p & 1): # n is a even number and can't be prime
        return False

    p1 = p - 1
    u = 0
    r = p1  # p-1 = 2**u * r

    while r % 2 == 0:
        r >>= 1
        u += 1

    # at this stage p-1 = 2**u * r  holds
    assert p-1 == 2**u * r

    def witness(a):
        """
        Returns: True, if there is a witness that p is not prime.
                False, when p might be prime
        """
        z = square_and_multiply(a, r, p)
        if z == 1:
            return False

        for i in range(u):
            z = square_and_multiply(a, 2**i * r, p)
            if z == p1:
                return False
        return True

    for j in range(s):
        a = random.randrange(2, p-2)
        if witness(a):
            return False

    return True

def generate_primes(n=512, k=1):
    """
    Generates prime numbers with bitlength n.
    Stops after the generation of k prime numbers.

    Caution: The numbers tested for primality start at
    a random place, but the tests are drawn with the integers
    following from the random start.
    """
    assert k > 0
    assert n > 0 and n < 4096

    # follows from the prime number theorem
    necessary_steps = math.floor( math.log(2**n) / 2 )
    # get n random bits as our first number to test for primality
    x = random.getrandbits(n)

    primes = []

    while k>0:
        if miller_rabin_primality_test(x, s=7):
            primes.append(x)
            k = k-1
        x = x+1

    return primes

def main():
    n = 2048
    primes = generate_primes(n=n)
    for p in primes:
        print('{} is prime with bitlength={}'.format(p, n))

if __name__ == '__main__':
    main()
```

Now we are finally capable to efficiently find large prime numbers and to complete the RSA Key Generation Algorithm. Below is the updated and fully working RSA Key Generation Algorithm. Below is the final RSA Key Generation Algorithm.

```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import eea
import random

def RSA_keygen(n=512):
    """
    Perform steps 1. to 5. in the RSA Key Generation process.
    """
    # step 1
    import generate_primes
    p = generate_primes.generate_primes(n=n, k=1)[0]
    q = generate_primes.generate_primes(n=n, k=1)[0]
    # step 2
    n = p * q
    # step 3
    phi_n = (p - 1) * (q - 1)
    # step 4 and step 5
    while True:
        e = random.randrange(1, phi_n-1)
        if math.gcd(e, phi_n) == 1:
            # step 5
            gcd, s, t = eea.EEA(phi_n, e)
            if gcd == (s*phi_n + t*e):
                d = t % phi_n
                break
    return (e, n, d)

if __name__ == '__main__':
    print(RSA_keygen())
```

## Conclusion
Creating large primes for the RSA cryptosystem is a matter of a 100 line Python Script. The only tools you need are some Algorithms from number theory and a textbook about Cryptography.
