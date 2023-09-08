import mysql.connector
from cryptography.fernet import Fernet
import os

db_config = {
    "host": "127.0.0.1",
    "port": "3306",
    "user": "root",
    "password": "password",  #fdvjk
    "database": "mydb"
}

try:
    db_connection = mysql.connector.connect(**db_config)
    db_cursor = db_connection.cursor()
    print("Connected to the MySQL database")

except Exception as err:
    print(f"Error: {err}")
    quit()

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


f = Fernet.generate_key()
key = Fernet(f)


print("Welcome to Password Manager")


def SaveCredentials(user_id, service, username, password):
    encrypted_password = key.encrypt(password.encode()).decode()
    query = "INSERT INTO credentials (user_id, service, username, encrypted_password) VALUES (%s, %s, %s, %s)"
    values = (user_id, service, username, encrypted_password)
    db_cursor.execute(query, values)
    db_connection.commit()
    print("Credentials are saved successfully")


def GetCredentials(user_id, service):
    query = "SELECT username, encrypted_password FROM credentials WHERE user_id = %s AND service = %s"
    db_cursor.execute(query, (user_id, service))
    result = db_cursor.fetchone()

    if result:
        username, encrypted_password = result
        decrypted_password = key.decrypt(encrypted_password.encode()).decode()
        return username, decrypted_password
    else:
        return None, None


def password_manager():
    while True:

        qns = input("if you are a verified user please signin or signup to continue   ").lower()

        while True:
            if qns == "signup":
                user_name_input = input("Create ur username: ")

                check_query = "SELECT user_name FROM users WHERE user_name = %s"
                cursor.execute(check_query, (user_name_input,))
                existing_user = cursor.fetchone()

                if existing_user:
                    print("Username already exists. Please choose a different username.")
                    continue

                user_password_input = input("Create ur password: ")
                encrypted_key = Fernet.generate_key()
                encrypted_password = key.encrypt(user_password_input.encode()).decode()
                query = "INSERT INTO users (user_name, encrypted_key, user_password) VALUES (%s, %s, %s)"
                values = (user_name_input, encrypted_key, encrypted_password)
                cursor.execute(query, values)
                conn.commit()

                user_id = cursor.lastrowid  # Fetch the last inserted user_id

                print("Sign up successful. You can now use your credentials to log in.")

                while True:
                    print("1. View")
                    print("2. Add")
                    print("3. Delete")
                    print("4. Exit")
                    option = input("Enter your option: ")

                    if option == '1':
                        profile = input("Do you want to view a particular profile's credentials or viwe all your saved "
                                        "credentials? All / profile ").lower()
                        if profile == "profile":
                            service = input("Enter your service name: ")
                            username, password = GetCredentials(user_id, service)
                            if username and password:
                                print(f"Your username: {username}")
                                print(f"Your password: {password}")
                            else:
                                print("Credentials not found")

                        elif profile == "all":
                            query = "SELECT service, username, encrypted_password FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            results = db_cursor.fetchall()
                            if not results:
                                print("No data available.")
                            else:
                                for result in results:
                                    service = result[0]
                                    username = result[1]
                                    encrypted_password = result[2]
                                    decrypted_password = key.decrypt(encrypted_password.encode()).decode()
                                    print(f"Service: {service} , Username: {username}, Password: {decrypted_password}")

                        elif profile != "profile" and "all":
                            print("Invalid option")

                        else:
                            quit()



                    elif option == '2':
                        service = input("Enter your service name: ")
                        username = input("Enter your username: ")
                        password = input("Enter your password: ")
                        SaveCredentials(user_id, service, username, password)


                    elif option == '3':
                        print("1. Delete a service's credentials")
                        print("2. Delete all credentials")
                        print("3. Delete user")

                        delete = input("Enter your delete option: ")

                        if delete == '1':

                            service = input("Enter the service name to delete credentials: ")
                            query = "DELETE FROM credentials WHERE user_id = %s AND service = %s"
                            db_cursor.execute(query, (user_id, service))
                            db_connection.commit()
                            if db_cursor.rowcount > 0:
                                print("Credentials deleted successfully")
                            else:
                                print("No credentials found for the specified service.")


                        elif delete == '2':
                            query = "DELETE FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()
                            if db_cursor.rowcount > 0:
                                print("Credentials deleted successfully")
                            else:
                                print("No credentials found for the specified service.")


                        elif delete == '3':
                            query = "DELETE FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()

                            query = "DELETE FROM users WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()
                            print("User deleted successfully")

                            break

                        else:
                            print("Invalid Option.")

                    elif option == '4':
                        print("Thank you!")
                        break

                break

            elif qns == "signin":
                user_name_input = input("Enter ur username: ")
                user_password_input = input("enter ur password: ")
                query = "SELECT user_id, user_name, user_password FROM users WHERE user_name = %s"
                cursor.execute(query, (user_name_input,))
                result = cursor.fetchone()

                if result:
                    user_id, db_user_name, encrypted_password = result
                    decrypted_password = key.decrypt(encrypted_password.encode()).decode()
                    if user_password_input == decrypted_password and user_name_input == db_user_name:
                        print("Access granted.")
                    else:
                        print("Access denied.")
                        continue
                else:
                    print("User not found.")
                    continue

                while True:
                    print("1. View")
                    print("2. Add")
                    print("3. Delete")
                    print("4. Exit")
                    option = input("Enter your option: ")

                    if option == '1':
                        profile = input("Do you want to view a particular profile's credentials or viwe all your saved "
                                        "credentials? All / profile ").lower()
                        if profile == "profile":
                            service = input("Enter your service name: ")
                            username, password = GetCredentials(user_id, service)
                            if username and password:
                                print(f"Your username: {username}")
                                print(f"Your password: {password}")
                            else:
                                print("Credentials not found")

                        elif profile == "all":
                            query = "SELECT service, username, encrypted_password FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            results = db_cursor.fetchall()
                            if not results:
                                print("No data available.")
                            else:
                                for result in results:
                                    service = result[0]
                                    username = result[1]
                                    encrypted_password = result[2]
                                    decrypted_password = key.decrypt(encrypted_password.encode()).decode()
                                    print(f"Service: {service} , Username: {username}, Password: {decrypted_password}")

                        elif profile != "profile" and "all":
                            print("Invalid option")



                        else:
                            quit()



                    elif option == '2':
                        service = input("Enter your service name: ")
                        username = input("Enter your username: ")
                        password = input("Enter your password: ")
                        SaveCredentials(user_id, service, username, password)


                    elif option == '3':
                        print("1. Delete a service's credentials")
                        print("2. Delete all credentials")
                        print("3. Delete user")

                        delete = input("Enter your delete option: ")

                        if delete == '1':
                            service = input("Enter the service name to delete credentials: ")
                            query = "DELETE FROM credentials WHERE user_id = %s AND service = %s"
                            db_cursor.execute(query, (user_id, service))
                            db_connection.commit()
                            if db_cursor.rowcount > 0:
                                print("Credentials deleted successfully")
                            else:
                                print("credentials not found for this service.")


                        elif delete == '2':
                            query = "DELETE FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()
                            if db_cursor.rowcount > 0:
                                print("Credentials deleted successfully")
                            else:
                                print("credentials not found.")


                        elif delete == '3':
                            query = "DELETE FROM credentials WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()

                            query = "DELETE FROM users WHERE user_id = %s"
                            db_cursor.execute(query, (user_id,))
                            db_connection.commit()
                            print("User deleted successfully")

                            break

                        else:
                            print("Invalid Option.")

                    elif option == '4':
                        print("Thank you!")
                        break

                    else:
                        print("Invalid option")

                break

            elif qns != "signin" or "signup":
                print("\nplease enter signin or signup\n")
                break

            else:
                quit()


password_manager()
db_cursor.close()
db_connection.close()
print("Database connection closed")
