#Som besökare vill jag kunna se en lista med auktionsobjekt (med kortfattad information).
SELECT title, info, end_time from objects;

#Som besökare vill jag kunna se en detaljsida per auktionsobjekt (och se mer detaljer).
SELECT * FROM objects WHERE object.id = chosen_id;

#KONTO
#Som besökare vill jag kunna registrera ett nytt konto och bli användare.
INSERT INTO users SET users.name = 'Karl', users.email = 'karl@gmail.com', users.password = 'abc123';

#Som användare vill jag kunna logga in.
SELECT * FROM users WHERE users.email = 'karl@gmail.com' AND users.password = 'abc123';

#AUKTIONSOBJEKT (2)
#Som användare vill jag kunna skapa nya auktionsobjekt.
INSERT INTO objects SET objects.title = 'Cool mugg', objects.start_time = CURRENT_TIMESTAMP, 
	objects.end_time = '2022-12-31 23:59:59', objects.description = 'cool mugg, snälla köp',
    objects.poster = 1, objects.info = 'Cool Mugg';

#Som användare vill jag att auktionsobjekt ska innehålla minst titel, beskrivning, starttid, sluttid och bild(er).
INSERT INTO images SET images.adress = 'cool_mugg.jpg', images.object = 1;
INSERT INTO images SET images.adress = 'cool_mugg2.png', images.object = 1;

UPDATE objects SET objects.info = 'Cool mugg, snälla köp', 
objects.description = 'Den här muggen är jättecool men jag har inte råd att behålla den. Den är värd mycket, snälla buda högt.'
WHERE objects.id = 1;

#BUD
#Som besökare vill jag kunna se nuvarande bud på auktionsobjekt i listvyer
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects
LEFT JOIN bids
ON objects.id = bids.object
GROUP BY objects.id;

#Som besökare vill jag kunna se de 5 senaste buden på auktionsobjekt i detaljsidor.
SELECT * FROM objects
WHERE objects.id = 1;

SELECT adress FROM images
WHERE images.object = 1;

SELECT * FROM bids
WHERE bids.object = 1
ORDER BY bids.amount DESC LIMIT 5;

#Som användare vill jag kunna lägga (högre än nuvarande) bud på auktionsobjekt, på dess detaljsida.
INSERT INTO bids SET bids.user = 4, bids.object = 1, bids.amount = 300, bids.date= CURRENT_TIMESTAMP;
SELECT MAX(bids.amount) FROM bids WHERE bids.object = 1;  

#Som användare ska jag inte kunna lägga bud på mina egna auktionsobjekt.
 SELECT objects.poster FROM objects WHERE objects.id = 1;
 
#Som användare vill jag kunna sätta ett utgångspris på mina auktionsobjekt.
INSERT INTO objects SET objects.title = 'Cool stol', objects.info = 'Coolaste stolen i stan', 
objects.start_time = CURRENT_TIMESTAMP, objects.end_time = '2023-01-01 11:00:00', objects.poster = 4,
objects.starting_price = 200, objects.description = 'Köp den coolaste stolen som finns.';
UPDATE objects SET objects.starting_price = 50 WHERE objects.id = 1; 

#Som användare vill jag kunna sätta ett dolt reservationspris på mina auktionsobjekt.
#(om bud ej uppnått reservationspris när auktionen avslutas så säljs objektet inte).;
UPDATE objects SET objects.reserve_price = 350 WHERE objects.id = 5; 

#Som besökare vill jag kunna se listor på auktioner inom olika kategorier.
CREATE TABLE categories;
INSERT INTO categories SET category = 'Books';
INSERT INTO categories SET category = 'Business & Industrial';
INSERT INTO categories SET category = 'Clothing, Shoes & Accessories';
INSERT INTO categories SET category = 'Collectibles';
INSERT INTO categories SET category = 'Consumer Electronics';
INSERT INTO categories SET category = 'Crafts';
INSERT INTO categories SET category = 'Dolls & Bears';
INSERT INTO categories SET category = 'Home & Garden';
INSERT INTO categories SET category = 'Motors';
INSERT INTO categories SET category = 'Pet Supplies';
INSERT INTO categories SET category = 'Sporting Goods';
INSERT INTO categories SET category = 'Sports Mem, Cards & Fan Shop';
INSERT INTO categories SET category = 'Toys & Hobbies';
INSERT INTO categories SET category = 'Antiques';
INSERT INTO categories SET category = 'Computers/Tablets & Networking';
# ADD CATEGORY TO OBJECTS, FILTER SELECT ON OBJECTS BY CATEGORY
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE objects.category = 3
GROUP BY objects.id;

#Som besökare vill jag kunna se listor på auktioner baserat på status (pågående, avslutade, sålda, ej sålda).
# ONGOING
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE CURRENT_TIMESTAMP BETWEEN objects.start_time AND objects.end_time
GROUP BY objects.id;
# FINISHED
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object
WHERE CURRENT_TIMESTAMP > objects.end_time
GROUP BY objects.id;
# SOLD
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object
WHERE CURRENT_TIMESTAMP > objects.end_time 
AND bids.amount > objects.starting_price AND bids.amount > objects.reserve_price
GROUP BY objects.id;
# UNSOLD
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object
WHERE CURRENT_TIMESTAMP BETWEEN objects.start_time AND objects.end_time
OR (CURRENT_TIMESTAMP > objects.end_time AND bids.amount < objects.reserve_price)
GROUP BY objects.id;

#Som användare vill jag kunna se en lista med mina egna auktionsobjekt.
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE OBJECTS.POSTER = 1
GROUP BY objects.id;

#Som användare vill jag kunna se en lista med auktionsobjekt jag har lagt bud på.
# SELECT * FROM OBJECTS WHERE OBJECTS.ID IN (SELECT BIDS.OBJECT FROM BIDS WHERE BIDS.USER = USER.ID)
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE objects.id IN 
	(SELECT bids.object FROM bids WHERE bids.user = 3)
GROUP BY objects.id;

#Som besökare vill jag kunna söka på auktioner baserat på vad jag skriver i ett sökfält.
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE objects.title LIKE '%rad%' 
OR objects.info LIKE '%rad%' 
OR objects.description LIKE '%rad%'
GROUP BY objects.id;

#Som besökare vill jag kunna söka på auktioner inom en kategori jag valt.
SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object 
WHERE (objects.title LIKE '%rad%' 
OR objects.info LIKE '%rad%' 
OR objects.description LIKE '%rad%')
AND category = 3
GROUP BY objects.id;

#Som köpare vill jag kunna ge ett betyg på köpet av ett auktionsobjekt.
INSERT INTO ratings SET ratings.rating = 5, ratings.user = 2;

#Som köpare vill jag kunna se säljares betyg när jag tittar på ett auktionsobjekt.
SELECT ROUND(AVG(ratings.rating), 1) FROM ratings WHERE ratings.user = 2; 

#Som användare vill jag kunna skicka meddelande till en säljare av ett auktionsobjekt.
INSERT INTO messages SET messages.sender = 1, messages.receiver = 2, messages.message = 'HEJ 2, detta är 1', messages.timestamp = CURRENT_TIMESTAMP;
INSERT INTO messages SET messages.sender = 2, messages.receiver = 1, messages.message = 'HEJ 1, detta är 2', messages.timestamp = CURRENT_TIMESTAMP; 

SELECT * FROM messages WHERE (sender = 1 AND receiver = 2) OR (sender = 2 AND receiver = 1)
ORDER BY messages.timestamp ASC;