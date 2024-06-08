import { InputHTMLAttributes, ReactNode, useState } from "react";
import { Button } from "../Button/Button";
import style from "./AuthForm.module.css";

export const AuthForm = (): ReactNode => {
  const [login, setLogin] = useState<string>();
  const [password, setPassword] = useState<string>();
  const [confirmPassword, setConfirmPassword] = useState<string>();
  const [isRegister, setFormType] = useState<boolean>();
  const onClick = () => {
    if (isRegister) {
      // send register query
    } else {
      // send auth query
    }
  };
  return (
    <div className={style.authFormWrapper}>
      <form className={style.authForm}>
        <input
          type="text"
          name="login"
          placeholder="Логин"
          onInput={(event: InputHTMLAttributes<HTMLInputElement>) =>
            setLogin(event.value?.toString())
          }
        />
        <input
          type="password"
          name="password"
          placeholder="Пароль"
          onInput={(event: InputHTMLAttributes<HTMLInputElement>) =>
            setPassword(event.value?.toString())
          }
        />
        {isRegister && (
          <input
            type="password"
            placeholder="Подтвердите пароль"
            onInput={(event: InputHTMLAttributes<HTMLInputElement>) =>
              setConfirmPassword(event.value?.toString())
            }
          />
        )}
        <Button isWide={true}>
          {isRegister ? "Зарегистрироваться" : "Авторизоваться"}
        </Button>
      </form>
      <Button isWide={true} onClick={() => setFormType(!isRegister)}>
        {isRegister ? "Уже есть аккаунт?" : "Нет аккаунта?"}
      </Button>
    </div>
  );
};
