
import React, { useState, useEffect, useRef } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView, Platform, SafeAreaView, Animated } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import axios from "axios";
import { API_URL } from "../config";

export default function LoginScreen({ navigation, onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // Animations
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  
  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 4,
        tension: 40,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

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
        
        console.log('Login response data:', JSON.stringify(userData, null, 2));
        
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
    <View style={styles.gradient}>
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView 
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.container}
        >
          <Animated.View 
            style={[
              styles.content,
              {
                opacity: fadeAnim,
                transform: [
                  { translateY: slideAnim },
                  { scale: scaleAnim }
                ]
              }
            ]}
          >
            {/* Logo/Icon */}
            <Animated.View style={[styles.logoContainer, { transform: [{ scale: scaleAnim }] }]}>
              <View style={styles.logoCircle}>
                <MaterialCommunityIcons name="face-recognition" size={56} color="#3b82f6" />
              </View>
            </Animated.View>

            {/* Title */}
            <View style={styles.titleContainer}>
              <Text style={styles.title}>Chấm công FaceID</Text>
              <Text style={styles.subtitle}>Đăng nhập để tiếp tục</Text>
            </View>

            {/* Login Form Card với BlurView */}
            <View style={styles.formCard}>
              <View style={styles.formInner}>
                {/* Username Input */}
                <View style={styles.inputWrapper}>
                  <Text style={styles.inputLabel}>Tên đăng nhập</Text>
                  <View style={[styles.inputContainer, username && styles.inputFocused]}>
                    <View style={styles.inputIconWrapper}>
                      <Ionicons name="person" size={20} color="#667eea" />
                    </View>
                    <TextInput
                      style={styles.input}
                      placeholder="Nhập tên đăng nhập..."
                      value={username}
                      onChangeText={setUsername}
                      placeholderTextColor="#94A3B8"
                      editable={!loading}
                      autoCapitalize="none"
                    />
                  </View>
                </View>

                {/* Password Input */}
                <View style={styles.inputWrapper}>
                  <Text style={styles.inputLabel}>Mật khẩu</Text>
                  <View style={[styles.inputContainer, password && styles.inputFocused]}>
                    <View style={styles.inputIconWrapper}>
                      <Ionicons name="lock-closed" size={20} color="#667eea" />
                    </View>
                    <TextInput
                      style={styles.input}
                      placeholder="Nhập mật khẩu..."
                      value={password}
                      onChangeText={setPassword}
                      secureTextEntry={!showPassword}
                      placeholderTextColor="#94A3B8"
                      editable={!loading}
                      autoCapitalize="none"
                    />
                    <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                      <Ionicons name={showPassword ? "eye" : "eye-off"} size={20} color="#64748B" />
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Login Button */}
                <TouchableOpacity
                  style={[styles.loginButton, loading && { opacity: 0.7 }]}
                  onPress={handleLogin}
                  disabled={loading}
                  activeOpacity={0.85}
                >
                  {loading ? (
                    <ActivityIndicator color="#fff" size="small" />
                  ) : (
                    <Text style={styles.loginButtonText}>Đăng nhập</Text>
                  )}
                </TouchableOpacity>
              </View>
            </View>

            {/* Footer */}
            <View style={styles.footer}>
              <MaterialCommunityIcons name="shield-check" size={18} color="#64748b" />
              <Text style={styles.footerText}>Bảo mật với công nghệ FaceID</Text>
            </View>
          </Animated.View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  gradient: { 
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  safeArea: {
    flex: 1,
  },
  container: { 
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center",
    padding: 24,
  },
  content: {
    width: '100%',
    maxWidth: 420,
    alignItems: 'center',
  },
  
  // Logo Styles
  logoContainer: {
    marginBottom: 32,
  },
  logoCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  
  // Title Styles
  titleContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  title: { 
    fontSize: 28, 
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: "#64748b",
    textAlign: 'center',
    fontWeight: '500',
  },
  
  // Form Card Styles
  formCard: {
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  formInner: {
    width: '100%',
  },
  
  // Input Styles
  inputWrapper: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: "#f8fafc",
    borderRadius: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  inputFocused: {
    borderColor: '#3b82f6',
    backgroundColor: '#fff',
  },
  inputIconWrapper: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#e0f2fe',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  input: { 
    flex: 1,
    height: 44,
    fontSize: 14,
    color: '#0f172a',
    fontWeight: '500',
  },
  eyeIcon: {
    padding: 8,
  },
  
  // Button Styles
  loginButton: {
    marginTop: 8,
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  loginButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  
  // Footer Styles
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
    gap: 8,
  },
  footerText: {
    color: "#64748b",
    fontSize: 12,
    fontWeight: '500',
  },
});