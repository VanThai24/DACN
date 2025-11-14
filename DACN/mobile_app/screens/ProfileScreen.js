import React, { useState, useEffect, useRef } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image, Modal, TextInput, Alert, ActivityIndicator, ScrollView, Animated } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { MaterialIcons } from '@expo/vector-icons';
import axios from "axios";
import { API_URL, SERVER_IP } from "../config";
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';
import { spacing } from '../theme/spacing';


export default function ProfileScreen({ user, onLogout }) {
  const [modalVisible, setModalVisible] = useState(false);
  const [editPhone, setEditPhone] = useState("");
  const [loading, setLoading] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 700,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 8,
        tension: 40,
        useNativeDriver: true,
      })
    ]).start();

    // Pulse animation for badge
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.15,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        })
      ])
    ).start();
  }, []);

  // Fallbacks for missing fields
  const name = user?.full_name || user?.name || user?.username || "(Không rõ)";
  const department = user?.department || user?.department_name || "(Chưa cập nhật)";
  const phone = user?.phone || user?.Phone || "(Chưa cập nhật)";
  const role = user?.role || "(Chưa cập nhật)";
  const email = user?.email || "(Chưa cập nhật)";
  
  // Xử lý avatar
  let avatar = user?.avatar;
  if (!avatar) {
    const photoPath = user?.photo_path || user?.photoPath;
    if (photoPath) {
      if (photoPath.startsWith("http")) {
        avatar = photoPath;
      } else if (photoPath.startsWith("/")) {
        avatar = `http://${SERVER_IP}:8000${photoPath}`;
      } else {
        avatar = `http://${SERVER_IP}:8000/photos/${photoPath}`;
      }
    }
  } else if (avatar.startsWith("/")) {
    avatar = `http://${SERVER_IP}:8000${avatar}`;
  }
  
  // Fallback với avatar placeholder theo chữ cái đầu
  if (!avatar) {
    avatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff&size=200`;
  }
  
  console.log('ProfileScreen - Avatar:', { 
    username: user?.username,
    user_avatar: user?.avatar,
    photo_path: user?.photo_path,
    final_avatar: avatar 
  });

  const handleUpdatePhone = async () => {
    if (!editPhone || editPhone.length < 10) {
      Alert.alert("Lỗi", "Vui lòng nhập số điện thoại hợp lệ (ít nhất 10 số)");
      return;
    }
    
    setLoading(true);
    try {
      await axios.put(`${API_URL}/employees/${user.id}`, {
        phone: editPhone
      });
      Alert.alert("Thành công", "Đã cập nhật số điện thoại!");
      user.phone = editPhone;
      setModalVisible(false);
    } catch (error) {
      Alert.alert("Lỗi", "Không thể cập nhật. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.gradient}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
          {/* Profile Header */}
          <Animated.View style={[styles.header, { transform: [{ scale: scaleAnim }] }]}>
            <View style={styles.avatarContainer}>
              <Image 
                source={{ uri: avatar }} 
                style={styles.avatar}
                onError={(e) => console.log('ProfileScreen - Avatar load error:', e.nativeEvent.error)}
                onLoad={() => console.log('ProfileScreen - Avatar loaded:', avatar)}
              />
              <Animated.View style={[styles.badge, { transform: [{ scale: pulseAnim }] }]}>
                <MaterialIcons name="verified" size={24} color="#3b82f6" />
              </Animated.View>
            </View>
            
            <Text style={styles.name}>{name}</Text>
            <Text style={styles.username}>@{user?.username}</Text>
          </Animated.View>
          
          {/* Profile Info Card */}
          <View style={styles.card}>
            <View style={styles.infoRow}>
              <View style={[styles.iconCircle, { backgroundColor: '#e0f2fe' }]}>
                <MaterialIcons name="badge" size={20} color="#3b82f6" />
              </View>
              <View style={styles.infoText}>
                <Text style={styles.label}>Họ tên</Text>
                <Text style={styles.value}>{name}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <View style={[styles.iconCircle, { backgroundColor: '#f3e8ff' }]}>
                <MaterialIcons name="business" size={20} color="#8b5cf6" />
              </View>
              <View style={styles.infoText}>
                <Text style={styles.label}>Phòng ban</Text>
                <Text style={styles.value}>{department}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <View style={[styles.iconCircle, { backgroundColor: '#fce7f3' }]}>
                <MaterialIcons name="work" size={20} color="#ec4899" />
              </View>
              <View style={styles.infoText}>
                <Text style={styles.label}>Chức vụ</Text>
                <Text style={styles.value}>{role}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <View style={[styles.iconCircle, { backgroundColor: '#d1fae5' }]}>
                <MaterialIcons name="phone" size={20} color="#10b981" />
              </View>
              <View style={styles.infoText}>
                <Text style={styles.label}>Số điện thoại</Text>
                <Text style={styles.value}>{phone}</Text>
              </View>
              <TouchableOpacity onPress={() => {
                setEditPhone(phone === "(Chưa cập nhật)" ? "" : phone);
                setModalVisible(true);
              }}>
                <MaterialIcons name="edit" size={20} color="#3b82f6" />
              </TouchableOpacity>
            </View>
            
            <View style={styles.infoRow}>
              <View style={[styles.iconCircle, { backgroundColor: '#fef3c7' }]}>
                <MaterialIcons name="email" size={20} color="#f59e0b" />
              </View>
              <View style={styles.infoText}>
                <Text style={styles.label}>Email</Text>
                <Text style={styles.value}>{email}</Text>
              </View>
            </View>
          </View>
          
          <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
            <MaterialIcons name="logout" size={20} color="#fff" />
            <Text style={styles.buttonText}>Đăng xuất</Text>
          </TouchableOpacity>
        </Animated.View>
      </ScrollView>

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Cập nhật số điện thoại</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <MaterialIcons name="close" size={28} color="#666" />
              </TouchableOpacity>
            </View>
            
            <TextInput
              style={styles.input}
              placeholder="Nhập số điện thoại mới"
              value={editPhone}
              onChangeText={setEditPhone}
              keyboardType="phone-pad"
              maxLength={15}
            />
            
            <TouchableOpacity 
              style={[styles.button, loading && { opacity: 0.6 }]}
              onPress={handleUpdatePhone}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <MaterialIcons name="check" size={20} color="#fff" />
                  <Text style={styles.buttonText}>Cập nhật</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  gradient: { 
    flex: 1, 
    backgroundColor: '#f8fafc',
  },
  scrollView: { flex: 1 },
  container: { 
    flex: 1, 
    paddingBottom: 24,
  },
  
  // Header Section
  header: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 32,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 16,
  },
  avatar: { 
    width: 120, 
    height: 120, 
    borderRadius: 60, 
    borderWidth: 4, 
    borderColor: '#fff',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  badge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    backgroundColor: '#fff',
    borderRadius: 50,
    padding: 4,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
    textAlign: 'center',
  },
  username: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 8,
    fontWeight: '500',
  },

  // Card Section
  card: { 
    backgroundColor: '#fff', 
    borderRadius: 16, 
    padding: 20, 
    marginHorizontal: 16,
    marginTop: 8,
    elevation: 2, 
    shadowColor: '#000', 
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08, 
    shadowRadius: 3 
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  infoText: {
    flex: 1,
  },
  label: { 
    fontSize: 11, 
    color: '#64748b',
    marginBottom: 4,
    textTransform: 'uppercase',
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  value: { 
    color: '#0f172a', 
    fontSize: 15,
    fontWeight: '600' 
  },
  logoutButton: { 
    backgroundColor: '#ef4444',
    marginTop: 24,
    marginHorizontal: 16,
    borderRadius: 12, 
    padding: 16, 
    alignItems: "center",
    flexDirection: 'row',
    justifyContent: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
  },
  button: { 
    width: "100%", 
    backgroundColor: '#3b82f6', 
    borderRadius: 12, 
    padding: 16, 
    alignItems: "center",
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
    elevation: 3,
  },
  buttonText: { 
    color: colors.white, 
    fontSize: typography.sizes.md, 
    fontWeight: typography.weights.bold,
    marginLeft: spacing.sm,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: spacing.borderRadius.xl,
    padding: spacing.xl,
    width: '88%',
    elevation: 20,
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
    paddingBottom: spacing.md,
    borderBottomWidth: 3,
    borderBottomColor: colors.primary.main,
  },
  modalTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.primary.main,
  },
  input: {
    backgroundColor: colors.gray[50],
    borderRadius: spacing.borderRadius.lg,
    padding: spacing.md,
    fontSize: typography.sizes.md,
    borderWidth: 2,
    borderColor: colors.gray[200],
    marginBottom: spacing.sm,
  },
});
