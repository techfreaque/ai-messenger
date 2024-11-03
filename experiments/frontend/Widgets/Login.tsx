import React, { useState } from "react";
import { Button, StyleSheet, TextInput } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

import { matrixClient } from "@/context/MatrixClient";

export default function Login(): JSX.Element {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { loginToMatrix, loginResponse } = matrixClient();

  const handleLogin = async (): Promise<void> => {
    await loginToMatrix(username, password);
  };
  console.log("resp", loginResponse);

  return (
    <SafeAreaProvider>
      <SafeAreaView>
        <TextInput
          style={styles.input}
          onChangeText={setUsername}
          value={username}
          placeholder='Enter your email'
          keyboardType='email-address'
          autoComplete='email'
        />
        <TextInput
          style={styles.input}
          onChangeText={setPassword}
          value={password}
          placeholder='Enter your password'
          autoComplete='current-password'
        />
        <Button title='Login' onPress={void handleLogin} />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  input: {
    height: 40,
    margin: 12,
    borderWidth: 1,
    padding: 10,
  },
});

// <div>
//   <h2>Login</h2>
//   <form>
//     {loginResponse && (
//       <div>Login Response: {JSON.stringify(loginResponse)}</div>
//     )}
//     <input
//       type='text'
//       value={username}
//       onChange={(e) => setUsername(e.target.value)}
//       placeholder='Matrix username'
//     />
//     <input
//       type='password'
//       value={password}
//       onChange={(e) => setPassword(e.target.value)}
//       placeholder='Password'
//     />
//     <button onClick={void handleLogin} type='submit'>
//       Login
//     </button>
//   </form>
//   {error && <p style={{ color: "red" }}>{error}</p>}
// </div>
