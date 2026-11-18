// File: app/(tabs)/feed.tsx
// Description: Display the selected profile's feed with author names and photos.

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

type Profile = {
  id: number;
  username: string;
  display_name: string;
};

type Photo = {
  id: number;
  post: number;
  image_url: string;
  image_file: string | null;
};

async function fetchFeedData(authFetch: AuthFetch, profileId: number) {
  const feedResponse = await authFetch(`${BASE_URL}/api/profile/${profileId}/feed`);
  const profilesResponse = await authFetch(`${BASE_URL}/api/profiles`);
  if (feedResponse.status !== 200 || profilesResponse.status !== 200) {
    throw new Error('Could not load your feed. Please refresh to try again.');
  }
  const posts: Post[] = await feedResponse.json();
  const profiles: Profile[] = await profilesResponse.json();
  let photos: Photo[] = [];
  for (const profile of profiles) {
    if (posts.some(post => post.profile === profile.id)) {
      const response = await authFetch(`${BASE_URL}/api/profile/${profile.id}/photos`);
      if (response.status !== 200) throw new Error('Could not load feed photos.');
      photos = photos.concat(await response.json());
    }
  }
  return { posts, profiles, photos };
}

export default function FeedScreen() {
  const { authFetch, profileId } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (profileId === null) return;
    const loadFeed = async () => {
      try {
        const data = await fetchFeedData(authFetch, profileId);
        setPosts(data.posts);
        setProfiles(data.profiles);
        setPhotos(data.photos);
      } catch {
        setMessage('Could not load your feed. Please refresh to try again.');
      } finally {
        setIsLoading(false);
      }
    };
    loadFeed();
  }, [authFetch, profileId]);

  const handleRefresh = async () => {
    if (profileId === null) return;
    setRefreshing(true);
    setMessage('');
    try {
      const data = await fetchFeedData(authFetch, profileId);
      setPosts(data.posts);
      setProfiles(data.profiles);
      setPhotos(data.photos);
    } catch {
      setMessage('Could not load your feed. Please refresh to try again.');
    } finally {
      setRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#295d91" />
        <Text style={styles.caption}>Loading your feed...</Text>
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
            <Text style={styles.titleText}>Your Feed</Text>
            <Text style={styles.bodyText}>Posts from the profiles you follow.</Text>
            <Button title="Refresh feed" onPress={handleRefresh} />
            {message ? <Text style={styles.messageText}>{message}</Text> : null}
          </View>
        }
        renderItem={({ item }) => {
          const author = profiles.find(profile => profile.id === item.profile);
          return (
            <View style={styles.card}>
              <Text style={styles.authorText}>{author ? author.display_name : 'Profile'}</Text>
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
          );
        }}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={<Text style={styles.bodyText}>No posts in your feed yet.</Text>}
        ListFooterComponent={<Text style={styles.listFooter}>End of your feed</Text>}
      />
    </View>
  );
}
