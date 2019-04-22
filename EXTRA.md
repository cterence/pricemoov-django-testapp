# Extra work


- I added some bootstrap CSS to make the whole thing look nice
- I added a `/first` route in order to initialize the database with an admin user
- I also added some security features including the impossibility to :
  - Edit the `is_admin` field when updating a non-admin user
  - Remove self admin privileges (to prevent the case where there is no admin in the database)