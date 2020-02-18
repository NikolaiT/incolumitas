Title: Probabilistic data structures to estimate cardinalities and frequencies of massive streams
Date: 2016-07-20 22:44
Modified: 2016-07-20 22:44
Author: Nikolai Tschacher
Category: BigData
Tags: LogLog-Count, Count-Min-Sketch, Linear Count, Big Data, Stream Processing
Slug: probabilistic-sketches-big-data
Status: published

In the following blog post we will introduce three different Big Data algorithms. More specifically, we will
learn about probabilistic data structures that allow us to estimate cardinalities and frequencies of
elements that originate from a massive stream of data. This blog post is heavily inspired by a the well written article on [probabilistic data structures for web analytics and data mining](https://highlyscalable.wordpress.com/2012/05/01/probabilistic-structures-web-analytics-data-mining/). I will not cover the mathematics behind those data structures, the beforementioned blog post does that much better. And if not, then you should probably consult the original papers.

### What is Big Data anyways?

Everybody talks nowadays about Big Data, but what does it mean? For example, if we want to count the number of distinct IP Addresses that a very large web site encounters on each day, we need new approaches. Consider the following straightforward algorithm:

```Python
unique_ip_addresses = set()
for ip in stream_of_ip_addresses:
    unique_ip_addresses.add(ip)
    if end_of_day(time):
        print('We got {} distinct ip addresses'.format(len(unique_ip_addresses)))
        unique_ip_addresses = set()
```

This way of counting distinct elements works fine for millions of visitors. But what happens if a website is visited 10 Billion times a day? Then we would need to maintain a set with space 10^10 * 4 Bytes = 40GB of RAM. Most normal computers simply don't have this huge amount of RAM. Additionally, the `add` operation on the set becomes slower and slower, because we need to search through the whole array to check whether we already added the element previously. In this blog post we need to simulate such a massive stream of ip addresses. We abstract from real elements and use simply integers. My stream implementation is very easy:

```Python
import random

class Stream:
    """
    Produces random elements and simulates a stream.
    """
    def __init__(self, n, rand_range):
        """
        n : Number of elements to produce.
        rand_range : Produced elements are in this random range.
        """
        self.n = n
        self.range = rand_range

    def produce(self):
        for i in range(self.n):
            yield random.randrange(*self.range)

    def __iter__(self):
        return self.produce()
```

### Counting distinct elements in a stream with much less space

There are data structures that allow us to determine the cardinality of a set with much less space than O(n). They can do so by trading accuracy against space consumption. Those data structures can estimate cardinalities within an acceptable margin of error by using much less space than O(n).

### Linear Counting

The idea behind the linear counter is to use a bitmask of length `m`. `m` is chosen to be around `m = n/5`. Then we use a hash function `h: n -> m`. Whenever an element arrives from the stream, we hash this element and use the hash result as an index to set in the bitmask. Then to count the cardinality, we compute the formula `-m * ln((m - sum(bitmask)) / m)`. This yields an estimation of the cardinality. This approach is implemented in the following pseudo code:

    :::python
    #!/usr/bin/env python3

    import random
    import math
    from stream import Stream

    class CardinalityCounter:

        def __init__(self, m):
            self.m = m
            # simulate the bitmask by using
            # a list with length m
            self.bitmask = self.m * [0]

        def hash(self, value):
            evenly_distributed = value * 19441 + 73877
            return evenly_distributed % self.m

        def add(self, value):
            hvalue = self.hash(value)
            self.bitmask[hvalue] = 1

        def get_cardinality(self):
            """
            Estimates the cardinality.
            """
            weight = sum(self.bitmask)
            if self.m == weight:
                raise Exception('Cannot estimate cardinality, weight equals m')
            return -self.m * math.log((self.m - weight) / self.m)

    def main():
        n = 100000
        randrange = (1, 1000000)
        m = 25000
        s = Stream(n, randrange)
        c = CardinalityCounter(m)
        real_cardinality = set()

        for a in s.produce():
            c.add(a)
            real_cardinality.add(a)

        real, est = len(real_cardinality), c.get_cardinality()
        error = abs(1 - (float(real)/est)) * 100
        print('Load factor is ', n/m)
        print('Estimated cardinality is ', est)
        print('Real cardinality is ', real)
        print('Error is: {0:.2f}%'.format(error))

    if __name__ == '__main__':
        main()

The problem with this approach is, that it consumes also `O(n)` space, although much less than a trivial counter implementation, because we use only around `n/5` **bits** (instead of n * 4 **Bytes** in the trivial algorithm). But we can do much better.

### LogLog Counter

The idea behind the LogLog Counter to estimate cardinalities is very beautiful: Whenever an element arrives from the data stream, we apply an hash function on it and visualize the hash value as bit string. In the example below, the hash value is only one Byte. In real life applications, it could be much larger.
```
Element 534 arrives: h(534) -> 00110011
Element 44 arrives: h(44) -> 10110010
Element 75 arrives: h(75) -> 11000110
...
Element n arrives: h(n) -> x
```

If the hash function distributes bits uniformly (as every good hash function should), we can expect that
```
1/2 of all hash values begin with an 1:     1.......
1/4 of all hash values begin with an 01:    01......
1/8 of all hash values begin with an 001:   001.....
...
1/2^k of all hash values begin with 0000...1
```

The first `1` of the binary representation of the hash value is defined as the rank of the hash value.

We can use this fact about uniform distributions to our advantage: We create `m` buckets. For every element of the stream that we encounter, we determine its bucket by the first `log(m)` bits of the hash value. With the remaining bits, we compute the rank. We update the bucket with this rank only if it is higher than the current rank. By doing so, we store the highest rank in those `m` buckets. If we have stored the rank 10 in some bucket `k`, then we know that on average we have already seen `2^k` distinct elements before. This beautiful idea is implemented in the Python code below. As a hash function, we chose `md5`. It is definitely not the best choice, since it is a cryptographic hash function and thus relatively slow.

    :::Python
    #!/usr/bin/env python3

    import random
    import math
    import hashlib
    import numpy as np
    from stream import Stream

    np.set_printoptions(threshold=np.inf)

    class LogLogCounter:
        def __init__(self, H, k, etype=8, n=100000):
            """
            H: length of hash function in bits
            k: number of bits that determine bucket
            etype: number of bits for each estimator (Not used yet)
            """
            self.H = H
            self.k = k
            self.etype = etype # currently ignored

            self.m = 2**self.k
            self.estimators = np.zeros(self.m, dtype=np.int8)
            self.hash_func_len = int(math.log(self.m, 2) + math.floor(math.log(n/self.m) + 3))

        def hash(self, value):
            """
            hashes the value and returns a 128 bit long bitstring.
            md5 is used, other hash functions might also work.
            """
            m = hashlib.md5()
            m.update(bytes(value))
            h = m.hexdigest()
            return '{0:0128b}'.format(int(h, 16))

        def get_bits(self, value, start, end, number=False):
            """
            Get a number from the bitstring specified by the range
            from start to end.
            """
            s = value[start:end]
            if number:
                return int(s, 2)
            else:
                return s

        def rank(self, value):
            """
            Find the position of the first '1' bit in the hash value.
            100...b has rank 1
            001...b has rank 3
            0000001...b has rank 7
            """
            try:
                return value.index('1') + 1
            except ValueError as e:
                return len(value)

        def add(self, value):
            hashed = self.hash(value)
            bucket = self.get_bits(hashed, 0, self.k, number=True)
            self.estimators[bucket] = max(
                self.estimators[bucket],
                self.rank(self.get_bits(hashed, self.k, self.H))
            )

        def estimate_cardinality(self):
            est_factor = 0.39701
            power = (1.0/self.m) * self.estimators.sum()
            est = est_factor * self.m * 2**power
            return int(est)

    def main():
        n = 100000
        randrange = (1, 1000000)
        s = Stream(n, randrange)
        real_card = set()
        loglogc = LogLogCounter(128, 10, 8, n)
        for a in s.produce():
            loglogc.add(a)
            real_card.add(a)

        real, est = len(real_card), loglogc.estimate_cardinality()
        error = abs(1 - (float(real)/est)) * 100
        print('Real cardinality={} and estimated cardinality={}'.format(real, est))
        print('Error is: {0:.2f}%'.format(error))

    if __name__ == '__main__':
        main()
