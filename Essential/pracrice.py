import secrets
import string

class PasswordGenerator:
  

    def __init__(self):
        self.lowercase_letters = string.ascii_lowercase
        self.uppercase_letters = string.ascii_uppercase
        self.digits = string.digits
        self.special_characters = string.punctuation

    def get_user_requirements(self):
        while True:
            try:
                self.length = int(input("Введите желаемую длину пароля: "))
                if self.length <= 0:
                    print("Длина пароля должна быть положительным числом. Попробуйте еще раз.")
                    continue
                break
            except ValueError:
                print("Некорректный ввод. Пожалуйста, введите целое число.")

        while True:
            use_special_chars_input = input("Использовать специальные символы? (да/нет): ").lower()
            if use_special_chars_input in ["да", "нет"]:
                self.use_special_chars = use_special_chars_input == "да"
                break
            else:
                print("Некорректный ввод. Пожалуйста, введите 'да' или 'нет'.")

    def generate_password(self):
        character_set = self.lowercase_letters + self.uppercase_letters + self.digits
        if self.use_special_chars:
            character_set += self.special_characters

        password = ''.join(secrets.choice(character_set) for _ in range(self.length))
        return password

def main():
    generator = PasswordGenerator()
    generator.get_user_requirements()
    generated_password = generator.generate_password()
    print("\nСгенерированный пароль:", generated_password)


if __name__ == "__main__":
    main()