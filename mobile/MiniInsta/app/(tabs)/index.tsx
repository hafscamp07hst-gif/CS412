// File: app/(tabs)/index.tsx
// Description: Retrieve the selected profile, its posts, and all of its photos.

import { useEffect, useState } from 'react';
import { ActivityIndicator, Button, FlatList, Image, Text, View } from 'react-native';
import { styles } from '../../assets/my_styles';
import { BASE_URL } from '../../constants/api';
import { useAuth, type AuthFetch } from '../../context/AuthContext';

type Post = {
  id: number;
  profile: number;
  caption: string;
  timestamp: string;
};

type Photo = {
  id: number;
  post: number;
  image_url: string;
  image_file: string | null;
};

async function fetchProfileData(authFetch: AuthFetch, profileId: number) {
  const profileResponse = await authFetch(`${BASE_URL}/api/profile/${profileId}`);
  const postsResponse = await authFetch(`${BASE_URL}/api/profile/${profileId}/posts`);
  const photosResponse = await authFetch(`${BASE_URL}/api/profile/${profileId}/photos`);
  if (profileResponse.status !== 200 || postsResponse.status !== 200 || photosResponse.status !== 200) {
    throw new Error('Could not load your profile. Please refresh to try again.');
  }
  return {
    profile: await profileResponse.json(),
    posts: await postsResponse.json(),
    photos: await photosResponse.json(),
  };
}

export default function ProfileScreen() {
  const { authFetch, profileId, logout } = useAuth();
  const [profile, setProfile] = useState({
    username: '', display_name: '', bio_text: '', profile_image_url: '', join_date: '',
  });
  const [posts, setPosts] = useState<Post[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (profileId === null) return;
    const loadProfile = async () => {
      try {
        const data = await fetchProfileData(authFetch, profileId);
        setProfile(data.profile);
        setPosts(data.posts);
        setPhotos(data.photos);
      } catch {
        setMessage('Could not load your profile. Please refresh to try again.');
      } finally {
        setIsLoading(false);
      }
    };
    loadProfile();
  }, [authFetch, profileId]);

  const handleRefresh = async () => {
    if (profileId === null) return;
    setRefreshing(true);
    setMessage('');
    try {
      const data = await fetchProfileData(authFetch, profileId);
      setProfile(data.profile);
      setPosts(data.posts);
      setPhotos(data.photos);
    } catch {
      setMessage('Could not load your profile. Please refresh to try again.');
    } finally {
      setRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#295d91" />
        <Text style={styles.caption}>Loading your profile...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={posts}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        ListHeaderComponent={
          <View style={styles.listHeader}>
            <Text style={styles.eyebrow}>MINI INSTA</Text>
            <Text style={styles.titleText}>{profile.display_name}</Text>
            {profile.profile_image_url ? (
              <Image source={{ uri: profile.profile_image_url }} style={styles.profileImage} resizeMode="cover" />
            ) : null}
            <Text style={styles.authorText}>@{profile.username}</Text>
            <Text style={styles.bodyText}>{profile.bio_text}</Text>
            <Text style={styles.caption}>Joined {profile.join_date.slice(0, 10)}</Text>
            <Text style={styles.sectionTitle}>My Posts</Text>
            <Button title="Refresh profile" onPress={handleRefresh} />
            <Button title="Log out" onPress={logout} />
            {message ? <Text style={styles.messageText}>{message}</Text> : null}
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.authorText}>@{profile.username}</Text>
            <Text style={styles.caption}>{item.timestamp.slice(0, 10)}</Text>
            <Text style={styles.postText}>{item.caption}</Text>
            {photos.filter(photo => photo.post === item.id).map(photo => (
              <Image
                key={photo.id}
                source={{ uri: photo.image_url || photo.image_file || '' }}
                style={styles.picture}
                resizeMode="contain"
              />
            ))}
          </View>
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={<Text style={styles.bodyText}>No posts yet. Create one in New Post.</Text>}
        ListFooterComponent={<Text style={styles.listFooter}>End of your posts</Text>}
      />
    </View>
  );
}
