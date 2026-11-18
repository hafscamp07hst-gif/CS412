// File: app/(tabs)/add_post.tsx
// Description: Collect a caption and create a post through the Django API.

import { useState } from 'react';
import { Button, ScrollView, Text, TextInput, View } from 'react-native';
import { styles } from '../../assets/my_styles';
import { BASE_URL } from '../../constants/api';
import { useAuth } from '../../context/AuthContext';

export default function AddPostScreen() {
  const { authFetch } = useAuth();
  const [caption, setCaption] = useState('');
  const [isPosting, setIsPosting] = useState(false);
  const [message, setMessage] = useState('');

  const addPost = async () => {
    if (caption === '') {
      setMessage('Please enter a caption.');
      return;
    }

    setIsPosting(true);
    setMessage('');
    try {
      const response = await authFetch(`${BASE_URL}/api/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ caption: caption }),
      });
      if (response.status === 201) {
        setCaption('');
        setMessage('Post created! Open My Profile and refresh to see it.');
      } else {
        setMessage('Could not create the post. Please try again.');
      }
    } catch {
      setMessage('Could not create the post. Please check the connection and try again.');
    } finally {
      setIsPosting(false);
    }
  };

  return (
    <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.eyebrow}>MINI INSTA</Text>
      <Text style={styles.titleText}>New Post</Text>
      <Text style={styles.bodyText}>Share a moment with a new caption.</Text>

      <View style={styles.inputCard}>
        <Text style={styles.labelText}>Caption</Text>
        <TextInput
          style={styles.input}
          placeholder="Write a caption"
          value={caption}
          onChangeText={setCaption}
        />
        <Button
          title={isPosting ? 'Submitting...' : 'Create post'}
          onPress={addPost}
          disabled={isPosting}
        />
      </View>

      {message ? <Text style={styles.messageText}>{message}</Text> : null}
    </ScrollView>
  );
}
