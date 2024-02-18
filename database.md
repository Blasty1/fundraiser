# Database Structure
1. User
    1. id_user  &rarr; integer ( primary key )
    2. email  &rarr; varchar(100)
    3. name  &rarr; varchar(100)
    4. surname  &rarr; varchar(100)
    6. password &rarr; varchar(100)
2. Fund
    1. Title &rarr; varchar(100)
    2. Description  &rarr; text ( optional )
    3. Image  &rarr; varchar(100)
    4. Target  &rarr; float
    5. Type  &rarr; varchar
    6. Max_donation  &rarr; float
    7. Min_donation  &rarr; float
    8. Start_timestamp  &rarr; timestamp
    9. End_timestamp  &rarr; timestamp
    10. id_fund  &rarr; integer ( primary key )
    12. id_user &rarr; integer ( foreign key )
3. Donation
    1. id_donation &rarr; integer ( primary key )
    3. id_fund  &rarr; integer ( foreign key )
    4. amount  &rarr; float
    5. created_at  &rarr; timestamp
    6. type  &rarr; varchar(100)
    7. Name &rarr; varchar(100)
    8. Surname  &rarr; varchar(100)
4. Wallet ( VIEW )
    1. id_fund &rarr; integer ( foreign key )
    2. id_user &rarr; integer ( foreign key )
    3. totalReached  &rarr; float
    4. created_at &rarr; timestamp




