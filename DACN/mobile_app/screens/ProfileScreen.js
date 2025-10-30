import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { LinearGradient } from "expo-linear-gradient";


export default function ProfileScreen({ user, onLogout }) {
  // Fallbacks for missing fields
  const name = user?.full_name || user?.name || user?.username || "(Không rõ)";
  const department = user?.department || user?.department_name || "(Chưa cập nhật)";
  const phone = user?.phone || user?.Phone || "(Chưa cập nhật)";
  const role = user?.role || "(Chưa cập nhật)";
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

  return (
    <LinearGradient colors={["#e3f0ff", "#f6f6f6"]} style={styles.gradient}>
      <View style={styles.container}>
        <Image source={{ uri: avatar }} style={styles.avatar} />
        <Text style={styles.title}>Thông tin cá nhân</Text>
        <View style={styles.card}>
          <Text style={styles.label}>Họ tên: <Text style={styles.value}>{name}</Text></Text>
          <Text style={styles.label}>Phòng ban: <Text style={styles.value}>{department}</Text></Text>
          <Text style={styles.label}>Số điện thoại: <Text style={styles.value}>{phone}</Text></Text>
          <Text style={styles.label}>Chức vụ: <Text style={styles.value}>{role}</Text></Text>
        </View>
        <TouchableOpacity style={styles.button} onPress={onLogout}>
          <Text style={styles.buttonText}>Đăng xuất</Text>
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  avatar: { width: 90, height: 90, borderRadius: 45, marginBottom: 18, borderWidth: 2, borderColor: "#2979ff" },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 18, color: "#2979ff" },
  card: { backgroundColor: "#fff", borderRadius: 16, padding: 18, borderWidth: 1, borderColor: "#e0e0e0", marginBottom: 20, elevation: 3, shadowColor: '#2979ff', shadowOpacity: 0.08, shadowRadius: 8 },
  label: { fontSize: 17, color: "#2979ff", fontWeight: "bold", marginBottom: 8 },
  value: { color: "#222", fontWeight: "normal" },
  button: { width: "80%", backgroundColor: "#2979ff", borderRadius: 8, padding: 14, alignItems: "center", marginTop: 10 },
  buttonText: { color: "#fff", fontSize: 18, fontWeight: "bold" },
});
