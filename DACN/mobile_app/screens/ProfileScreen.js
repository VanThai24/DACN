import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image, Modal, TextInput, Alert, ActivityIndicator, ScrollView } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { MaterialIcons } from '@expo/vector-icons';
import axios from "axios";
import { API_URL } from "../config";


export default function ProfileScreen({ user, onLogout }) {
  const [modalVisible, setModalVisible] = useState(false);
  const [editPhone, setEditPhone] = useState("");
  const [loading, setLoading] = useState(false);

  // Fallbacks for missing fields
  const name = user?.full_name || user?.name || user?.username || "(Không rõ)";
  const department = user?.department || user?.department_name || "(Chưa cập nhật)";
  const phone = user?.phone || user?.Phone || "(Chưa cập nhật)";
  const role = user?.role || "(Chưa cập nhật)";
  const email = user?.email || "(Chưa cập nhật)";
  
  // Ưu tiên lấy avatar từ user.avatar, nếu không có thì lấy user.photo_path hoặc user.photoPath
  let avatar = user?.avatar;
  if (!avatar) {
    avatar = user?.photo_path || user?.photoPath;
    // Nếu là đường dẫn tương đối, thêm domain
    if (avatar && avatar.startsWith("/")) {
      avatar = `http://${user?.server_ip || '192.168.110.45'}:8000${avatar}`;
    }
  }
  if (!avatar) avatar = "https://randomuser.me/api/portraits/men/32.jpg";

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
    <LinearGradient colors={["#667eea", "#764ba2"]} style={styles.gradient}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.container}>
          {/* Profile Header */}
          <View style={styles.header}>
            <View style={styles.avatarContainer}>
              <Image source={{ uri: avatar }} style={styles.avatar} />
              <View style={styles.badge}>
                <MaterialIcons name="verified" size={28} color="#667eea" />
              </View>
            </View>
            
            <Text style={styles.name}>{name}</Text>
            <Text style={styles.username}>@{user?.username}</Text>
          </View>
          
          {/* Profile Info Card */}
          <View style={styles.card}>
            <View style={styles.infoRow}>
              <MaterialIcons name="badge" size={24} color="#2979ff" />
              <View style={styles.infoText}>
                <Text style={styles.label}>Họ tên</Text>
                <Text style={styles.value}>{name}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <MaterialIcons name="business" size={24} color="#2979ff" />
              <View style={styles.infoText}>
                <Text style={styles.label}>Phòng ban</Text>
                <Text style={styles.value}>{department}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <MaterialIcons name="work" size={24} color="#2979ff" />
              <View style={styles.infoText}>
                <Text style={styles.label}>Chức vụ</Text>
                <Text style={styles.value}>{role}</Text>
              </View>
            </View>
            
            <View style={styles.infoRow}>
              <MaterialIcons name="phone" size={24} color="#2979ff" />
              <View style={styles.infoText}>
                <Text style={styles.label}>Số điện thoại</Text>
                <Text style={styles.value}>{phone}</Text>
              </View>
              <TouchableOpacity onPress={() => {
                setEditPhone(phone === "(Chưa cập nhật)" ? "" : phone);
                setModalVisible(true);
              }}>
                <MaterialIcons name="edit" size={20} color="#2979ff" />
              </TouchableOpacity>
            </View>
            
            <View style={styles.infoRow}>
              <MaterialIcons name="email" size={24} color="#2979ff" />
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
        </View>
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
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  scrollView: { flex: 1 },
  container: { 
    flex: 1, 
    paddingBottom: 30,
  },
  
  // Header Section
  header: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 30,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: 20,
  },
  avatar: { 
    width: 130, 
    height: 130, 
    borderRadius: 65, 
    borderWidth: 5, 
    borderColor: "#fff",
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  badge: {
    position: 'absolute',
    bottom: 5,
    right: 5,
    backgroundColor: '#fff',
    borderRadius: 18,
    padding: 4,
    elevation: 4,
  },
  name: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 6,
    textAlign: 'center',
  },
  username: {
    fontSize: 16,
    color: '#ffffff90',
    marginBottom: 8,
  },

  // Card Section
  card: { 
    backgroundColor: "#fff", 
    borderTopLeftRadius: 32, 
    borderTopRightRadius: 32, 
    padding: 24, 
    width: '100%',
    minHeight: 400,
    elevation: 8, 
    shadowColor: '#2979ff', 
    shadowOpacity: 0.08, 
    shadowRadius: 8 
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f5f5f5',
    backgroundColor: '#fafafa',
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  infoText: {
    flex: 1,
    marginLeft: 16,
  },
  label: { 
    fontSize: 13, 
    color: "#999",
    marginBottom: 4,
    textTransform: 'uppercase',
    fontWeight: '500',
  },
  value: { 
    color: "#1a1a1a", 
    fontSize: 17,
    fontWeight: "600" 
  },
  logoutButton: { 
    width: "100%", 
    backgroundColor: "#e53935",
    marginTop: 20,
    borderRadius: 16, 
    padding: 16, 
    alignItems: "center",
    flexDirection: 'row',
    justifyContent: 'center',
    elevation: 2,
  },
  button: { 
    width: "100%", 
    backgroundColor: "#2979ff", 
    borderRadius: 12, 
    padding: 16, 
    alignItems: "center",
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
  },
  buttonText: { 
    color: "#fff", 
    fontSize: 17, 
    fontWeight: "bold",
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 24,
    width: '85%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 2,
    borderBottomColor: '#2979ff',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2979ff',
  },
  input: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    marginBottom: 8,
  },
});
