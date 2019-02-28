README
============

These are some files that I completely own and not really bound by any NDA.

## Components

* Components are independent modules tightly bound to a network entity, for example, our player entities.
* They have their own independent logic, and corresponding client logic.
* Storage wise, their database entry is appended with the primary key with their parent entity.
* They provide a layer of isolation and reusability.
* Different components on one entity can directly communicate with each other.

## Data

* StaticData objects are provides context compared to raw data. 
* Its stored in our redis cache layer and provides shared data to all of our users
* We can add validation checks, as well as other parsing, indexing and searching functions based on data.

## HexGrid

* HexGrid is the logical representation of our game world.
* Broken down into chunks and cells.