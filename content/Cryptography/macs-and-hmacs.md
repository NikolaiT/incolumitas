Title: Cryptographic properties of MACs and HMACs
Date: 2018-08-20 21:53
Modified: 2018-08-20 22:00
Author: Nikolai Tschacher
Category: Security, Cryptography, MAC, HMAC
Tags: Math, MAC, HMAC
Slug: cryptographic-properties-mac-and-hmac
Status: published

## Introduction
Similarly as digital signatures, **Message Authentication Codes** provide message integrity and message authentication. When Alice generates a MAC and sends the message and MAC to Bob, Bob verifies that the message has integrity by calculating the MAC himself. He also authenticates the message, because only Alice could have generated the MAC.

Unlike digital signatures they do however not provide nonrepudiation, since all involved parties share the secret key $k$. MAC's can be implemented using cryptographically secure hash functions (HMAC) or symmetric block ciphers like AES.

A MAC consists of a set of messages $X$, a finite set of hash values $Y$ and a key space $K$. Each key $k$ specifies a hash function $h_k: X \rightarrow Y$. Let $n=|X|$ and $m=|Y|$ and $l=|K|$.

Each MAC must have a property known as **computation resistance**: Even if an attacker knows $n$ text-hash pairs $(x_n, h_k(x_n))$, it remains computationally unfeasible to find a valid MAC for a message without knowledge of the used key $k$.

The goal of an attacker is to compute a valid MAC for a message $x \in X$ without knowing the secret key $k$. There are a series of different attack categories:

+ **Impersonation: **The attacker knows only which MAC is used and tries to generate a valid MAC with the unknown key $k$. He tries to act like a person who owns the key.
+ **Substitution: ** The attacker knows the MAC value for one message $x$ and tries to find a valid MAC for another message $x'$ such that $x \notin x'$.
+ **Known-text attack: ** The attacker knows for a bunch of texts $x_1, ..., x_r$ he has not chosen himself the corresponding MAC values. He tries to generate a new MAC for a new message $x' \notin \{x_1, ..., x_r\}$
+ **Chosen-text attack: ** The attacker can choose the texts himself.
+ **Adaptive chosen-text attack: ** The attacker can chose a text for which he receives a MAC under the knowledge of the previous MACs.

## Information Theoretic Security of MACs (After Shannon)
The underlying model is that keys $k$ and messages $x$ are generated independent from each other such that $p(k \cap x) = p(k)p(x)$.

#### Impersonation Success Probability
Let $\alpha$ be the probability that an Oscar can pretend to be Alice without Bob realizing it. The probability $p(x \rightarrow y)$ is the probability that a random message maps to the MAC value. This is the same as the sum of all probabilities that we randomly pick a key that maps the message to the MAC value. $\alpha(x) = \text{max}\{\alpha(x,y)|y \in Y\}$

It is easy to see that $\alpha(x) \geq \frac{1}{m}$ where $m$ the size of the set of all possible MACs. When $\chi$ is a random variable and has values in the positive real numbers, then $$log(E(\chi)) \geq E(log(\chi))$$

Then for each $MAC_h(x)=y$ the following inequality holds $$\alpha \geq \frac{1}{2^{H(K)-H(K|X,Y)}} \geq 1/l$$ This inequality makes a statement about the impersonation probability $\alpha$ given the entropy $H$. $\alpha$ becomes smaller while the key distribution becomes more uniform. The smaller the conditional entropy $H(K|X,Y)$, the smaller becomes the impersonation probability $\alpha$. $H(K|X,Y)$ measures the entropy of the key distribution $K$ that is not revealed by $X$ and $Y$.

Entropy is a measurement of uncertainty of outcome. For example the entropy $H$ of $n$ independent coin tosses is $n$, since $n$ coin tosses can be encoded with a bitstring of length $n$. **Entropy** is defined over a discrete random variable $X$ $$H(X) = -\sum_{x \in X}(Pr(x)*log_2(Pr(x)))$$ Note that the logarithm of a probability is negative, and thus the whole sum is multiplied again with $-1$ to obtain a positive value.

**Jensens inequality** plays also a big role in information theory. Let $f$ be a continuous strictly concave function (like the $log$ function) and $A$ be a probability distribution. Then
$$\sum_{i=1}^{n}a_if(x_i) \leq f(\sum_{i=1}^{n}a_ix_i)$$

We can derive with the above results that $H(X,Y) \leq H(X)+H(Y)$ with equality only if $X$ and $Y$ are **independent random variables**.

Now we can define **conditional entropy**. Conditional entropy $H(X|Y)$ measures the average amount of information about the random variable $X$ that is not revealed by $Y$.
$$H(X|Y) = -\sum_{y \in Y}\sum_{x \in X}Pr(y)Pr(x|y)log(Pr(x|y))$$

#### Substitution Success Probability
Let $\beta$ be the substitution success probability that he manages to substitute a fixed message $x$ with $x'$. Then the success probability is $p(x' \rightarrow y' | x \rightarrow y)$. The maximal success probability of substitution can be denoted as $$\beta(x,y) = \text{max } p(x' \rightarrow y' | x \rightarrow y)$$.

The lower bound of success is the same as for $\alpha$: $\beta(x,y) \geq 1/m$

A MAC is called **2-universal** if $$|K(x,y,x',y')| = \frac{|K|}{m^2}$$ For 2-universal MACs it holds that $|K| \geq m^2$ A MAC has substitution success probability $\beta=\frac{1}{m}$ exactly then when he is 2-universal. Then also $\alpha = \frac{1}{m}$.

A simple example for a 2-universal MAC is $h_{a,b}(x) = ax + b \mod p$ where $(a,b) \in Z \times Z$ and $p$ is prime.

To obtain a MAC with compression functionality, once can use a construction such as
$$h_k(x) = kx = \sum_{i=1}^d k_ix_i \mod p$$ where $d$ is the size of the vector for $(x_1,...,x_d)$ and $(k_1,...,k_d)$

## HMAC
Intuitively one would create a HMAC in one of the following ways $MAC_k(x) = h(k||x)$ or $MAC_k(x) = h(x||k)$  However those constructions suffer from weaknesses.

### Attack on $MAC_k(x) = h(k||x)$
Let's assume $h$ uses the Merkle Damgård Construction. Alice creates the MAC $m$ for a message $x=x_1||...||x_n$. Then an attacker can append an arbitrary message block $x_{n+1}$ to $x$ and receives a valid MAC $m' = MAC_k(m, x_{n+1})$. Thus the attacker can create valid MACS for messages he already knows the MAC for. The attacker controls what comes after the original message.

### Attack on $MAC_k(x) = h(x||k)$
If we find a collision for $x$ such that $h(x)=h(x')$, then $MAC_k(x) = MAC_k(x') = h(x||k) = h(x'||k)$ because the iterative nature of the Merkle Damgård Construction and that the message after x and x' is identical.

### Better HMAC
Knowing the difficulties of HMAC creation, if we construct a HMAC like $$HMAC_k(x)=h((k \oplus \text{ opad })||h((k \oplus \text{ ipad })||x))$$ with the $k$ being left padded with zeros to match the block size $b$. Usually **SHA-1** is used as $h$. The padded key is then XORed with ipad and opad, where $\text{ipad}=36||...||36$ and $\text{opad}=5C||...||5C$ are 512 bit constants of a repetitive bit pattern with length 64. $f = h((k \oplus \text{ ipad })||x)$ is a keyed hash function that hashes arbitrarily sized inputs and $g = h((k \oplus \text{ opad })||y)$ takes a input of exactly 512 bit.

When $f$ is collision resistant and $g$ is computation resistant, HMAC is computation resistant.

When there is no adaptive $(\epsilon_1,q+1)$ collision attack on $f$ and no adaptive $(\epsilon_2,q)$ forgery for $g$, then there is no $(\epsilon_1+\epsilon_2,q+1)$ forgery for the HMAC.

It can be proven that the HMAC construction above is secure if the used hash function is collision free. So in order to break the HMAC, one must find collisions for the used hash function (For example SHA-2).

## CBC-MAC
One can also create hashes with block ciphers such as with AES used in cipher block chaining mode (CBC). MAC creation is simply the repeated encryption of the message blocks XORed with the previous result of the encryption (Similarly as the sponge construction). The initial encryption uses a random and public IV.
$$y_1 = e_k(x_1 \oplus IV)$$ to start and
$$y_i = e_k(x_i \oplus y_{i-1})$$ takes each message block $x_i$ and XORs it with the output of the previous round. Then the final MAC is set as the final result of all encryptions $MAC_k(x) = y_n$

There is an **adaptive chosen text attack** on a CBC-MAC when CBC-MACs are used without preprocessing. If the attacker knows the MAC values $z=h_k(x)$ and $z'=h_k(x')$ for the texts $x=x_1||...||x_n$ and $x'=(x_{n+1} \oplus IV \oplus z)||x_{n+2}||...||x_{n+m}$, then the MAC value $h_k(x'') = z'$ for the message $x''=x_1||...||x_{n+m}$.

This attack is not possible if only messages with fixed lengths $nt$ are allowed.

There is also an **birthday attack** on CBC-MACs where you need $q \approx 2^{t/2}$ queries to obtain the MAC value for an message $x$ that was not queried before. $x$ can be arbitrarily chosen, except the first t-bit-block is given. $x$ is a $tn$ long bitstring. The attacker chooses $n-2$ arbitrary t-bit-blocks and two times $q$ pairwise-different t-bit-blocks. He then queries the MAC values $z_i = h_k(x^i)$ for the selected messages. If there is a collision pair for the computed MACs, he will find them.

The above described attack is a $(\epsilon, q+1)$-Attack for $q \approx 1.17\cdot2^{t/2}$. Only the last query is adaptive, all the $q$ prior are non adaptive.

In general there are **adaptive queries**, where the query $x_i$ depends on the queries $x_1, ..., x_{i-1}$ before. Non-adaptive queries do not need knowledge about the prior queries. Then there are **selective forgeries**, where the attacker can obtain the MAC value for a message he has chosen. Then there are **existential forgeries**, where the attacker can obtain a forgery but cannot chose which one.
