
import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from "react-native";
import axios from "axios";
import { API_URL } from "../config";

export default function LoginScreen({ navigation, onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (loading) return;
    setLoading(true);
    // Kiểm tra kết nối server trước
    try {
      await axios.get(API_URL + "/", { timeout: 3000 });
    } catch (err) {
      setLoading(false);
      Alert.alert("Lỗi", "Không thể kết nối server. Vui lòng kiểm tra lại mạng hoặc server.");
      return;
    }
    // Nếu server phản hồi, tiếp tục đăng nhập
    try {
      const res = await axios.post(
        API_URL + "/auth/login",
        { username, password },
        { timeout: 7000 }
      );
      if (res.data.id && res.data.username) {
        setLoading(false);
        if (onLogin) onLogin(res.data); // Pass user info to parent
        else navigation.replace("Home");
      } else {
        setLoading(false);
        Alert.alert("Đăng nhập thất bại", "Sai thông tin đăng nhập");
      }
    } catch (err) {
      setLoading(false);
      if (err.code === 'ECONNABORTED') {
        Alert.alert("Lỗi", "Kết nối server quá lâu, vui lòng thử lại.");
      } else {
        Alert.alert("Lỗi", "Không thể kết nối server");
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Đăng nhập</Text>
      <TextInput
        style={styles.input}
        placeholder="Tên đăng nhập"
        value={username}
        onChangeText={setUsername}
        placeholderTextColor="#888"
        editable={!loading}
      />
      <TextInput
        style={styles.input}
        placeholder="Mật khẩu"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        placeholderTextColor="#888"
        editable={!loading}
      />
      <TouchableOpacity
        style={[styles.button, loading && { opacity: 0.6 }]}
        onPress={handleLogin}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Đăng nhập</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#f6f6f6" },
  title: { fontSize: 28, fontWeight: "bold", marginBottom: 30, color: "#222" },
  input: { width: "80%", backgroundColor: "#fff", borderRadius: 8, padding: 14, marginBottom: 14, fontSize: 17, borderWidth: 1, borderColor: "#e0e0e0" },
  button: { width: "80%", backgroundColor: "#2979ff", borderRadius: 8, padding: 14, alignItems: "center", marginTop: 10 },
  buttonText: { color: "#fff", fontSize: 18, fontWeight: "bold" },
});
