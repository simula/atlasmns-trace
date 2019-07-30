use atlasmnsdb
db.dropUser("atlasmnsimporter")
db.dropUser("atlasmnsresearcher")
db.createUser({ user: "atlasmnsimporter",   pwd: "!importer!",   roles: [ "readWrite" ] })
db.createUser({ user: "atlasmnsresearcher", pwd: "!researcher!", roles: [ "dbAdmin", "readWrite" ] })
