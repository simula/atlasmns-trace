use atlasmnsdb

// ====== Create collections ================================================
db.createCollection("atlasmns", { storageEngine: { wiredTiger: { configString: 'block_compressor=zlib' }}})
db.createCollection("ripeatlastraceroute", { storageEngine: { wiredTiger: { configString: 'block_compressor=zlib' }}})
show collections

// ====== Create indices ====================================================
db.atlasmns.createIndex( { timestamp: 1 })
db.ripeatlastraceroute.createIndex( { timestamp: 1 })
