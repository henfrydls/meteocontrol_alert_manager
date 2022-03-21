from cryptography.fernet import Fernet

class Password:
    def password_manager(self, password : str) -> tuple:
        """This function recieved a password and encrypted it"""
        # generate a key for encryption and decryption
        key = Fernet.generate_key()

        fernet = Fernet(key)
        encpassword = fernet.encrypt(password.encode())

        # Return encpassword and key in tuple
        return (encpassword, password, key)


    def password_solver(self, encpassword: str, key: str) -> str:
        """A function to decrypt password"""
        # Instance the Fernet class with the key
        fernet = Fernet(bytes(key))
        
        return(fernet.decrypt(encpassword).decode())