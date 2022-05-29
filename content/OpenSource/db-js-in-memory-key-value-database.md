Title: db.js — In-Memory Key-Value Database with Persistant File Storage
Date: 2022-05-29 12:36
Category: Open Source
Tags: db.js, in-memory database, key-value storage, JSON file persistance
Slug: db.js-in-memory-key-value-database-with-persistant-file-storage
Summary: Instead of using one of the many battle proofed and reliable database solutions out there, I rather created my own solution. In this quick blog post, I am announcing the release of `db.js` - A in-memory database with persistant file storage.
Author: Nikolai Tschacher
Status: Published

<a class="btn" href="https://github.com/NikolaiT/db.js/" style="padding: 10px; font-size: 16px;">Find db.js on GitHub</a>

# Design Principles

From the many programming projects (often API's) I have created in the past, I observed that I always need to persist data to disk in order to query/update it later. Quite frequently, I found myself (re)creating quick & dirty persistance logic. I usually store everything as JSON on disk. I don't like to use SQL databases if I don't have to.

Of course I could use something like [Memcached](https://memcached.org/) or [Redis](https://redis.io/). Or even a SQL database service such as [PostgreSQL](https://www.postgresql.org/). To be honest, Memcached or Redis would have been a better solution.

<img src="{static}/images/no_thanks.jpeg" alt="No thanks" style="border: 1px solid #767575;" />

Having discussed reinventing the wheel and that I like doing it, let's focus on the design principles and the capabilities that I need from `db.js`:

1. **In-Memory**: Recently stored data should be kept in an in-memory cache, since recent data is read and updated way more frequently than old data. This observation is **paramount!**
2. **Key-Value semantics:** I like to associate the stored object with an unique key. Therefore, I like to work with key-value storages.
3. **JSON Format**: I like to store data as JSON in files, since the performance benefits of other data formats don't outweight the easiness to work with JSON. Put differently: I just don't have the time to learn any other data format than JSON. JSON is easily readable and that's what matters most. Everyone understands JSON. There are other things such BSON, but no one really cares about it.
4. **Persistance:** I don't want to care about when/why/where to persist data. This should be done by `db.js` in the background in a safe and consistent manner. Data is persisted to simple JSON files after the memory-cache reaches a certain age or size.
5. **No SQL required:** No complex SQL query semantic is needed. In fact, the only way I need to query data is:
    + base on a key with lookup time `O(1)`
    + based on a time range `(ts0, ts1)` where `ts0` and `ts1` are both timestamps
    + based on an index range `(start, stop)` where `start` and `stop` are both integers
    + if I don't specify any selection criteria, then `db.js` should just return the memory cache contents (lookup time `O(1)`)
6. **Data does not need to be deleted:** I don't care about deleting data. Delete operations are hard to implement, since a delete operation requires an index and reverse index update. In fact, providing a delete operation doesn't outweigh the complexity introduced by its implementation.

# Quick Start & Usage

`db.js` allows you to work with key/value data without caring about data persistance and storage. All that `db.js` gives you is a key/value store. `db.js` persists data to disk as JSON files periodically and safely. Currently `db.js` does not run as a daemon, it will shut down safely when the process is terminated.

Installation:

```
npm install https://github.com/NikolaiT/db.js
```

Simple Usage:

```js
const DBjs = require('./index').DBjs;

let db_js = new DBjs();

db_js.set('4343', {'name': 'test'});

console.log(db_js.get('4343'));

db_js.close();
```

## More Realistic Example

Obviously, using `db.js` like above does not make much sense. I use `db.js` mostly as data storage for the many web API's I am creating. Therefore, the following example using express is more useful:

```js
const express = require('express')
const DBjs = require('./dbjs').DBjs

let db_js = new DBjs();

const app = express()
const port = 3000

function randomString(length = 100) {
    let str = '';
    for (let i = 0; i < length; i++) {
        str += String.fromCharCode(Math.floor(65 + Math.random() * 25));
    }
    return str;
}

// Setting keys: http://localhost:3000/set?key=alpha&value=beta
// Getting value for a key: http://localhost:3000/get?key=alpha

app.all('/set', (req, res) => {
    res.header('Content-Type', 'application/json');

    if (req.query.key === undefined) {
        return res.status(400).send({ msg: 'you must provide a key' })
    }

    let key = req.query.key;
    let value = undefined;

    if (req.query.value) {
        value = req.query.value
    }

    if (req.body && req.body.value) {
        value = req.body.value;
    }

    if (value === undefined) {
        return res.status(400).send({ msg: 'you must provide a value' })
    }

    db_js.set(key, value);

    return res.status(200).send({ msg: 'ok' })
})

app.get('/get', (req, res) => {
    res.header('Content-Type', 'application/json');

    if (req.query.key === undefined) {
        return res.status(400).send({ msg: 'you must provide a key' })
    }

    let key = req.query.key;

    return res.status(200).send(db_js.get(key))
})

app.get('/get_all', (req, res) => {
    res.header('Content-Type', 'application/json');
    return res.status(200).send(JSON.stringify(db_js._getn(100000), null, 2))
})

app.get('/insert_random', (req, res) => {
    res.header('Content-Type', 'application/json');

    if (req.query.num === undefined) {
        return res.status(400).send({ msg: 'you must provide the number of random values to insert with the key `num`' })
    }

    let num = parseInt(req.query.num);

    for (let i = 0; i < num; i++) {
        db_js.set(randomString(5), randomString(30));
    }

    return res.status(200).send({ msg: 'ok' })
})

app.listen(port, () => {
    console.log(`Example db.js app listening on port ${port}`)
})
```

# db.js API

The db.js API currently has five main API methods:

#### set(key, value)

`set(key, value)` - Assigns the `value` to the `key` in the storage. If the `key` is already in the database, the value will be overwritten. keys are unique.

#### get(key)

`get(key)` - Returns the `value` associated with `key` from the storage. The lookup time is `O(1)`.

#### getn(index_range, time_range)

`getn(index_range, time_range)` - Returns an array of values in insertion order. This means that the most recent inserted value (Inserted with `set(key, value)`) is returned as first element of the array. When both `index_range=null` and `time_range=null` are set to `null`, then `getn()` returns the memory cache contents by default.

The variable `index_range` selects values to be returned by index range. If you specify `index_range=[0, 500]`, then the last 500 inserted values are returned.

The variable `time_range` selects values to be returned by an timestamp range. If you specify `time_range=[1649418657952, 1649418675192]`, then the items that were inserted between those two timestamps will be returned.

#### index_size()

`index_size()` - Returns the index size of the database. This is equivalent to the number of all database entries and thus the size of the database.

#### cache_size()

`cache_size()` - Returns the cache size of the database. The cache includes all database entries that are kept in memory.