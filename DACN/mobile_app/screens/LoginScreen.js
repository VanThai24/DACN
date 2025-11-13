
import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView, Platform, SafeAreaView } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from '@expo/vector-icons';
import axios from "axios";
import { API_URL } from "../config";

export default function LoginScreen({ navigation, onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
        let userData = res.data;
        
        // 🔥 Nếu backend không trả employee_id, mặc định bằng user.id
        // (Backend cần được fix để trả đúng employee_id)
        if (!userData.employee_id) {
          console.warn('Backend did not return employee_id, using user.id as fallback');
          // Không hardcode nữa - để frontend xử lý
        }
        
        setLoading(false);
        if (onLogin) onLogin(userData);
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
    <LinearGradient colors={["#667eea", "#764ba2"]} style={styles.gradient}>
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.container}
        >
          <View style={styles.content}>
            {/* Logo/Icon */}
            <View style={styles.logoContainer}>
              <View style={styles.logoCircle}>
                <Ionicons name="finger-print" size={60} color="#667eea" />
              </View>
            </View>

            {/* Title */}
            <Text style={styles.title}>Chấm công FaceID</Text>
            <Text style={styles.subtitle}>Đăng nhập để tiếp tục</Text>

            {/* Login Form Card */}
            <View style={styles.formCard}>
              {/* Username Input */}
              <View style={styles.inputContainer}>
                <Ionicons name="person-outline" size={22} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Tên đăng nhập"
                  value={username}
                  onChangeText={setUsername}
                  placeholderTextColor="#999"
                  editable={!loading}
                  autoCapitalize="none"
                />
              </View>

              {/* Password Input */}
              <View style={styles.inputContainer}>
                <Ionicons name="lock-closed-outline" size={22} color="#667eea" style={styles.inputIcon} />
                <TextInput
                  style={styles.input}
                  placeholder="Mật khẩu"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                  placeholderTextColor="#999"
                  editable={!loading}
                  autoCapitalize="none"
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                  <Ionicons name={showPassword ? "eye-outline" : "eye-off-outline"} size={22} color="#999" />
                </TouchableOpacity>
              </View>

              {/* Login Button */}
              <TouchableOpacity
                style={[styles.loginButton, loading && { opacity: 0.7 }]}
                onPress={handleLogin}
                disabled={loading}
                activeOpacity={0.8}
              >
                <LinearGradient colors={["#667eea", "#764ba2"]} style={styles.loginGradient}>
                  {loading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <>
                      <Text style={styles.loginButtonText}>Đăng nhập</Text>
                      <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginLeft: 8 }} />
                    </>
                  )}
                </LinearGradient>
              </TouchableOpacity>
            </View>

            {/* Footer */}
            <View style={styles.footer}>
              <Ionicons name="shield-checkmark" size={18} color="#ffffff90" />
              <Text style={styles.footerText}>Bảo mật với công nghệ FaceID</Text>
            </View>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { 
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  container: { 
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center",
    padding: 20,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  logoContainer: {
    marginBottom: 30,
  },
  logoCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 10,
  },
  title: { 
    fontSize: 32, 
    fontWeight: "bold", 
    color: "#fff",
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: "#ffffff90",
    marginBottom: 40,
    textAlign: 'center',
  },
  formCard: {
    width: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: "#f8f9fa",
    borderRadius: 16,
    marginBottom: 16,
    paddingHorizontal: 16,
    borderWidth: 2,
    borderColor: '#f0f0f0',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: { 
    flex: 1,
    height: 56,
    fontSize: 16,
    color: '#1a1a1a',
  },
  eyeIcon: {
    padding: 8,
  },
  loginButton: {
    marginTop: 8,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
  },
  loginGradient: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 16,
  },
  loginButtonText: { 
    color: "#fff", 
    fontSize: 18, 
    fontWeight: "bold",
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 32,
  },
  footerText: {
    color: "#ffffff90",
    fontSize: 14,
    marginLeft: 8,
  },
});
