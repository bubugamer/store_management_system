CREATE TABLE "products" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL,
	"category"	TEXT NOT NULL,
	"brand"	TEXT,
	"status"	INTEGER NOT NULL,
	"cost_price"	REAL,
	"supplier"	TEXT,
	"list_price"	REAL,
	"sales_price"	REAL,
	"salesperson"	TEXT,
	"unit"	TEXT,
	"specification"	TEXT,
	"barcode"	TEXT,
	"remark"	TEXT,
	"attribute1"	TEXT,
	"attribute2"	TEXT,
	"attribute3"	TEXT,
	"attribute4"	TEXT,
	"attribute5"	TEXT,
	"in_time"	DATETIME,
	"out_time"	DATETIME,
	"abandonment_time"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT)
)

commit;