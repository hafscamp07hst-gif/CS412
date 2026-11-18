// File: components/LoginScreen.tsx
// Description: Log in using the Django token API and the shared AuthContext.

import { useState } from 'react';
import { Button, ScrollView, Text, TextInput, View } from 'react-native';
import { styles } from '../assets/my_styles';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [message, setMessage] = useState('');

  const handleLogin = async () => {
    if (username === '' || password === '') {
      setMessage('Please enter your username and password.');
      return;
    }
    setIsLoggingIn(true);
    setMessage('');
    try {
      await login(username, password);
      setPassword('');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not log in. Please try again.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  return (
    <ScrollView style={styles.scrollView} contentContainerStyle={[styles.scrollContent, { paddingTop: 80 }]}>
      <Text style={styles.eyebrow}>MINI INSTA</Text>
      <Text style={styles.titleText}>Log in</Text>
      <Text style={styles.bodyText}>Sign in to see your profile, posts, and feed.</Text>
      <View style={styles.inputCard}>
        <Text style={styles.labelText}>Username</Text>
        <TextInput
          style={styles.input}
          placeholder="Username"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <Text style={styles.labelText}>Password</Text>
        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
        />
        <Button title={isLoggingIn ? 'Logging in...' : 'Log in'} onPress={handleLogin} disabled={isLoggingIn} />
      </View>
      {message ? <Text style={styles.messageText}>{message}</Text> : null}
    </ScrollView>
  );
}
