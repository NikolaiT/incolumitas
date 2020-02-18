Title: Cryptographic Hash Functions
Date: 2018-08-18 21:39
Modified: 2018-08-19 15:00
Author: Nikolai Tschacher
Category: Security, Cryptography, Hash Functions
Tags: Math, Integrity, Hash-Functions, Merkle-Damgård
Slug: cryptographic-hash-functions
Status: published

## Introduction
This blog post will introduce cryptographic hash functions. We are going to discuss the **Merkle-Damgård construction** which underlies many hash functions that were and are used nowadays. The **MD4, MD5, SHA-1 and SHA-2** hash families are all functions that built on top of the **Merkle-Damgård construction**. Then we will introduce an alternative construction that was popularized during the publication of **Keccak (SHA-3)**: The **Sponge construction**.

But what are cryptographic hash functions good for?

The general idea is to apply a unique and stable fingerprint to each input data $x$. This fingerprint is computed with a hash function $h$ and the resulting value $y = h(x)$ is called a message digest. The size of $h(x)$ is fixed, even though the input data $x$ may have arbitrary length. The intended task for $h$ is to assign a unique identification code $h(x)$ for each input $x \in X$ where $X$ is the set of all possible inputs. The avid reader might realize that this task is impossible, since there is no bijective function that connects an infinite large input set $X$ with fixed sized output set $h(x)$. Thus there must be collisions: For some inputs $x_1 \neq x_2 \in X: h(x_1) = h(x_2)$. It turns out that the whole fuzz in hash function security revolves around whether there are collisions for a hash function and how they can be found.

The security services that are achieved with hash functions are:

+ **Message authentication: ** This security service makes sure that a message is not altered in transmission. This property is also called **Integrity**. This property additionally ensures that the sender of the message unequivocally created the message. Only he knows what $x$ must have been, since only $h(x)$ was transmitted.
+ **Entity authentication: ** Enables entities to verify themselves.

Hash functions without keys are sometimes also called Manipulation Detection Codes (MDC). As the name suggests, their main task is to ensure **Integrity**. Note that a MITM attacker *Oscar* can replace $(x, h(x))$ with his own MDC $(x', h(x'))$ and *Bob* has no way to recognize that this message didn't originate from *Alice*.

If Alice wants to authenticate her message, she must use a **Message Authentication Code (MAC)**. A MAC is essentially a hash function that cryptographically hashes a message together with a symmetric key: $y = h_k(x)$. Alice and Bob must share a identical secret key $k$. They can obtain secret keys $k$ by using a asymmetric key exchange protocol like **Diffie-Hellman Key Exchange** that is based on public key cryptography. Now when Alice sends her MAC $(x, h_k(x)$ to Bob and Oscar replaces the message with $(x, h_{\tilde{k}}(x)$ using his own key $\tilde{k}$ Bob can detect that the message was illegally tampered with since $h_{\tilde{k}}(x) \neq h_k(x)$. For this reason the message is said to be authenticated as long as Alice and Bob share a secret key $k$. When Bob receives a MAC $(x', MAC)$ and Bob verifies $MAC = h_k(x')$, Bob can be sure that Alice created the message, because only Alice and him own the secret key $k$.

## Keyless Hash Functions (MDC)
We assume in the following chapter that $h$ is a publicly known hash function such as MD5 or SHA-1. Some definitions and symbols introduced:

+ $h: X \rightarrow Y$ is the hash function where $X$ is the set of all possible messages and $Y$ is the set of all possible hash values. $\bigm| X \bigm| = n$ and $\bigm| Y \bigm| = m$
+ If $X$ is finite, we require that $n \geq 2m$ and we call $h$ a **compression function**. This makes intuitive sense since $X$ is at least double the size of $Y$ and $h$ compresses the elements of $X$ into the smaller set $Y$.

Now the main requirement for hash functions is the one-wayness of $h$. This means that a $y = h(x)$ can be easily computed given a message $x$, but the reverse, to find a $x$ given a message digest $$x=f^{-1}(y)$$ should be computationally unfeasible to achieve.

We introduce now the **required security properties for hash functions**

### 1. Preimage Resistance (One-Way hash function)
It must be computationally unfeasible to find a message $x \in X$ given $y=h(x)$. For example, if you find the password hashes in `/etc/shadow`, it must be computationally unfeasible to find a matching $x$ such that $y=h(x)$.

In the real world, your best attack would be to just try a word-list attack. But if the password $x$ was truly randomly chosen and is 512 bits long, you will not recover $x$ from $y$ in this or in the next thousand generations unless $h$ is flawed (and not preimage resistant).
### 2. Second Preimage Resistance (Weak Collision Resistance)
It must be computationally unfeasible to find a $x' \in X \backslash {x}$ such that $h(x') = h(x)$ given a text $x$ and $y=h(x)$. In words: Given a $x$, it is computationally hard to find another $x'$ that computes to the same hash value. Note that $x \neq x'$.
### 3. Strong Collision Resistance
It must be computationally unfeasible to find two messages $x, x' \in X$ such that $h(x) = h(x')$. Note that $x \neq x'$.

### Comparison of Security Properties
Note that strong collision resistance is a much tougher security property to achieve, since the attacker can choose any $x$ and $x'$ (Two degrees of freedom). Second preimage resistance instead fixes $x$ and requires the attacker to find another $x'$ that hashes to the same value as $x$ (1 degree of freedom).

It can be proofed that strong collision resistant hash functions are preimage resistant and weakly collision resistant.

It's obvious that a strongly collision resistant hash function is also weakly collision resistant, since we can just fix all $x \in X$ and for each fixed message, the hash function is weakly collision resistant.

But why is a strong collision resistant hash function also preimage resistant (one-way function)? If your hash function is strongly collision resistant, you won't be able to compute any $x, x' \in X$ such that $h(x) = h(x')$. Therefore you also won't find any $x$ such that $y=h(x)$. (Proof needed.)

### The Random Oracle Model (ROM)
We introduce a model where we obtain an upper bound of the resources needed to launch an attack against hash functions $h$. The ROM gives us an idealized cryptographic hash function such that we obtain a random function $h: X \rightarrow Y$ from all possible $m^n$ functions.

This means that an attacker gets to know how the hash function works only if he asks the ROM for the hash values of a series of messages. Because the ROM creates a random hash function, it remains hard to predict $h(x)$ if the attacker receives a series of hash values for some messages. In reality, $h$ is not random and the attacker does know how the hash functions work. However, those public functions are intended to behave like a ROM.

Therefore the ROM requires that the probability that $Pr(h(x)=y|h(x_i) = y_i \text{ for } i=1,..,k) = \frac{1}{m}$. In words: Even though the attacker knows $k$ hash values for $k$ texts, he cannot predict any better what the next text $x_{k+1}$ hashes to than $1/m$.

Now what is the probability of an attacker in the ROM to find an pre-image for some $y=h(x)$?

If the attacker Oscar queries the ROM $q$ times with messages $\{x_1, x_2, ..., x_q\}$ and the probability to query with a *correct* $x_i$ remains $1/m$ (as suggested), then the probability to **not find an pre-image q times** is $(1-\frac{1}{m})^q$. The probability to find such a pre-image is $$1-(1-\frac{1}{m})^q \approx q/m$$ The probability too find a second pre-image (weak collision resistance) is accordingly $$1-(1-\frac{1}{m})^{q-1} \approx q/m$$

To get a $50%$ chance to find a pre-image, you need to query the ROM with $q=m/2$ queries. When the hash function has a output length of $2^{160}$, you will need to query $2^{159}$ times.

#### Attack on Collision Resistance with Birthday Paradox
The birthday paradox demonstrates a way to attack hash functions with strong collision resistance. It states that the probability to find a collision $(x, x')$ is $$p=1-\frac{(m-1)(m-2)\cdot...\cdot(m-q+1)}{m^{q-1}}$$ when you query the ROM with $q$ messages $x_1, ..., x_q$.

This makes intuitively sense, since the probability to find a collision depends on whether the comparison between any possible pairs of your queries message digest yields a tuple $(x, x')$ for which $h(x) = h(x')$. The $q+1$ time you query the ROM you have a probability of about $q/m$ that there is a collision. The $q+2$ time the probability rises to $\frac{q+1}{m}$. This observation can be written formally as $$p = 1 - \frac{m-1}{m}\cdot\frac{m-2}{m} \cdot\cdot\cdot \frac{m-q+1}{m}$$ For what $q$ do we achieve a probability for a collision of $0.5$?

Let $p$ be the probability to find a collision after $q$ queries. Let $$1-x \approx e^{-x}$$Then $p = 1-\prod_{i=1}^{q-1} \left(1-i/m\right) = ... = 1-e^{-\frac{q^2}{2m}} = q^2/2m$ and we see $$p = q^2/2m \Leftrightarrow q = \sqrt{p \cdot 2m}$$

When p is close to zero, we obtain an estimation for $q$ as $$q \approx c\sqrt{m}$$ with some constant $c=1.17$.

This essentially means that with the **Birthday Attack**, to obtain a fifty-fifty chance to find a collision, we need to query the ROM $\sqrt{2^m} = 2^{m/2}$ times where $m$ is the bitlength of the hash function. For example, you need to calculate $2^{128/2} = 2^{64}$ MD5 hashes to find any collision. This is totally feasible nowadays.

### Merkle-Damgård Construction and Iterated Hash functions
Given a collision resistant compression function $$h: \{0,1\}^{m} \times \{0,1\}^{t}  \rightarrow \{0,1\}^{m}$$ the goal of iterated hash functions (such as the Merkle-Damgård Construction) is to create a collision-resistant hash function $\tilde{h}$ $$\tilde{h}: \{0,1\}^{\ast} \rightarrow \{0,1\}^{l}$$ that hashes arbitrary sized messages to a message digest of bitlength $l$. Note that the compression function takes two inputs, one with bitlength $m$ and one with bitlength $t$.

In words: The main task of the Merkle-Damgård Construction (MD) is too extend the domain of a collision free compression function to arbitrary sized messages. MD divides arbitrary sized messages into fixed blocks and adds a secure padding (preprocessing step). Then MD uses the output of the compression function of one block as the input together with the next block for a new iteration of the compression function until all blocks have been processed (processing step). Formally, those steps can be written as:

+ **Preprocessing: **Transform any input $x \in \{0,1\}^{\ast}$ into $r$ blocks of size $t$ such that the transformed string $y(x) = y_1||y_2||...||y_r$ is dividable by $t$: $|y(x)| \equiv_t 0$ As we will see, MD adds a certain padding in the preprocessing step in order for the construction to be secure.
+ **Processing: ** $\text{IV}$ is a publicly known initialization vector of size $m$ ($m$ zero Bits in the case of MD). We compute a series of values $z_0, z_1, ..., z_r$ by calling the compression function $r$ times such that $$z_0 = \text{IV}$$ and $$z_i = h(z_{i-1} || y_i)$$
+ **Final Step: ** Output $z_r$ as the final hash value, then $m=l$. Optionally transform $z_r$ with a final transformation function $\text{transform}: \{0,1\}^{m} \rightarrow \{0,1\}^{l}$

We want the preprocessing function $y$ to be **suffix free**, because we can then prove that our final hash function $\tilde{h}$ is collision resistant. In other words: The goal is to prove that we can find a collision in the hash function only if we can find a collision in the compression function.

Our preprocessing function $y$ is suffix free, if there are no strings $x \neq x', z \in \{0,1\}^{\ast}$ such that $y(x) = z||y(x')$. A suffix in computer science is usually something added at the end of a string, such as the file ending `.txt`.

$y$ would **NOT** be suffix free, if messages would just be padded with constant zeroes in order to form a message that is a multiple of $t$: $|y(x)| \equiv_t 0$.

Example: If $t=8 \text{ Bytes}$ and we have the two messages $x=\text{Hello} \neq x'=\text{Hello00}$ and pad them with our zero padding, we obtain a collision $y(x) = y(x')$ even though $x \neq x'$. Therefore zero padding is a insecure padding.

There are many Merkle-Damgård complient padding schemes. The original padding scheme is **length-padding**, whereby $r$ blocks of size $t$ are created. The first bit of each block is always 1 (except in the first block, there the first bit is a 0). In the $(r-1)\text{th}$ block of the padding we fill the remaining space with exactly $d$ zero bits. In the $r\text{-th}$ block we binary encode the length of $d$. Alternatively we can binary encode the length of the whole message in the last block. It's the same, because $d$ is a function of the size of the message.

In short, **length-padding** transforms an input message in such a way that there are $r$ blocks of size $t$ and the next to last block is filled with zero bits in order to obtain a length of the block size $t$. The last block is a binary representation of the original message length. The message length encoding must be at a fixed position in the last block to be resistant against length extension attacks.

It turns out that length encoding is the simplest form of a padding that is suffix free. You can read the formally correct proof here: [Characterizing Padding Rules of MD Hash Functions
Preserving Collision Security](https://eprint.iacr.org/2009/325.pdf).

The informal proof sketch is taken from [stackexchange](https://crypto.stackexchange.com/questions/1427/why-does-the-padding-in-merkle-damg%C3%A5rd-hash-functions-like-md5-contain-the-messa). Assume we have a collision in our hash function. We show that there must be a collision in the underlying compression function if two distinct inputs are length-padded (and thus suffix free).

+ If the distinct messages have different length, then a collision in the compression function must occur in the last block, because the last block holds the binary length of the message and the length is different, even though the value of the compression function is identical.
+ If the messages are of the same length, then there is a well defined rightmost block in the MD-chain where the messages differ, but the output of the compression function is equal. Thus the collision is in the compression function. It can be shown with induction that somewhere in the chain must be two distinct inputs to the compression function which yields an identical output.

### Hash Functions based on the Merkle-Damgård Construction
MD4, MD5, SHA-1 and SHA-2 are all based on the MD construction. MD4 and MD5 use little endian representation of words, SHA uses big endian. The compression function of MD4 (1990) is broken, it's possible to find collisions after $2^{20}$ queries to the ROM. MD5 (1991) is a improved version of MD4, with an additional fourth round and other constants in the compression function. MD5 is also not collision resistant anymore and shouldn't be used any longer.

SHA-1 is also based on MD construction and is the successor of the MD4, MD5 family. Instead of 132 bit output length, SHA-1 has 160 bit output length. SHA-1 is still in use today and is still considered more or less secure.

In 2001 and 2004 NIST published 224, 256, 384 and 512 bit variants of the SHA family. They are regarded as the SHA-2 family. The output length varies and the internal functionality such as the number of rounds/shift amounts/constants of the compression function is different to SHA-1.

In 2012 Keccak (SHA-3) was presented as the successor of SHA-1 and SHA-2. Although SHA-2 is still considered secure, SHA-3 is build on a completely different architecture than the Merkle-Damgård Construction. The idea is to have a strong and standardized hash function that doesn't builds on the MD construction.

### Sponge Construction and Keccak (SHA-3)
The sponge construction is the internal architecture of the SHA-3 hash function. It can be used to compute a hash value or to generate pseudo-random bits. Keccak can be divided into two phases:

+ **Absorbing phase**: Message blocks are passed to the algorithm.
+ **Squeezing phase**: Output of configurable length is computed. When Keccak is used as SHA-3, only $y_0$ of $y_0...$_n$ is taken from the output.

Illustration of the sponge construction (Image from Wikipedia):

![sponge construction](https://upload.wikimedia.org/wikipedia/commons/7/70/SpongeConstruction.svg)

Instead of using a compression function, the sponge construction uses internally a permutation $$f: \{0,1\}^b \rightarrow \{0,1\}^b$$ which is iteratively applied. $b = r+c$ whereby $c$ is called the capacity and considered to be the internal state of the sponge construction. $r$ is called the bit rate and is equal to the length of a message block. $r$ is also said to be the external state of the sponge, because only the first $r$ bits are extracted in the squeezing phase.

For SHA-3 a state of $b=1600$ bits is used. The two combinations $(r,c) = (1344, 256)$ and $(r,c) = (1088, 512)$ are allowed.

Before the actual sponge construction can be used, a message is padded with a sponge conform padding function. The padding function $\text{pad}$ essentially looks like $$\text{pad(m)} = m||P10^{\ast}1$$ The padding function appends a bit string $P$ followed by zero or more zeros terminated by a 1 at the input message $m$. $P$ depends on the mode and the output length. After the padding, the padded message is a multiple of the bit length $k \cdot r$ where $k$ is the number of blocks.

The actual sponge construction can be defined for a sponge conform padding $y$, a permutation $f$. Let $x \in \{0,1\}^{\ast}$ and let $y(x) = y_1, y_2, ..., y_k$ with length of $|y_i|=r$. We define the states $s_i, i \geq 0:$

$$s_i = 0^b, \text{ if } i=0$$ which initializes the sponge construction and
$$s_i = f(s_{i-1} \oplus (y_i||0^c)), \text{ if } 1 \leq i \leq k$$ which is called the **Absorbing Phase** which XORs the result from the previous permutation with the current message block $y_i$ padded with $c$ zero bits. Then follows
$$s_i = f(s_{i-1}), \text{ if } i > k$$ which is called the **Squeezing phase**. When only the first result from the **Squeezing phase** is used, we obtain a SHA-3 value. The further results may be used as pseudo-random numbers.

The actual results from the sponge construction are the first $r$ bits from the squeezing phase $z_i = s_{k+i-1}$ for $i \geq 1$. Because r is either $1088$ or $1344$, only as many bits as required for the intended security level are taken.

It can be shown that to obtain a inner collision, you must evaluate $q \approx c \cdot 2^{c/2}$ hash values. $c$ is either 256 or 512 and thus sufficiently large. Pre-image resistance is also $min(c/2, n)$ where n is the chose output length. This is the roughly the same as what can be achieved with the birthday attack.

The permutation function $f$ consists of seven bijective functions that manipulate the state. The internal state of Keccak can be represented as a $5x5xw$ cube where $w$ is the wordsize of Keccak and $w=64$. Therefore the functions can be written as $$f: \{0,1\}^{5x5x64} \rightarrow \{0,1\}^{5x5x64}$$

It's not of particular interest how the permutation function works. Readers who are interested can read a very nice introduction of [Christof Paar here](https://pdfs.semanticscholar.org/8450/06456ff132a406444fa85aa7b5636266a8d0.pdf).
