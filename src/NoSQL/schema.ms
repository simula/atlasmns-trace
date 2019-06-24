use atlasmnsdb

// ====== Create collections ================================================
db.createCollection("atlasmns", { storageEngine: { wiredTiger: { configString: 'block_compressor=zlib' }}})
show collections

// ====== Create indices ====================================================
db.atlasmns.createIndex( { timestamp: 1 })
