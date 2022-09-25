# RazBot
The repo for the new (in dev) version of RazBot

## Todo:
### Reaction roles:
Idea: Store reaction roles in a database and query database on reaction add/remove event. Issue could be the amount of DB queries just for that.  
* Reaction role system is complete.

### Permissons system:
OG Idea: I was thinking having discord permissons (like kick/ban) override RazBot permissons. But allow setup of differnet roles to do tasks that discord permissons don't cover. Also allow setting of "full access" users but this may not bypass certain admin checks, like clear all data commands etc..
* Permission system basics are layed out. Fetches from the database and caches the result in memory to make commmands run faster.
