import React from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from "expo-linear-gradient";

const { height } = Dimensions.get('window');

export default function HomeScreen() {
  return (
    <LinearGradient colors={["#e3f0ff", "#f6f6f6"]} style={styles.gradient}>
      <View style={styles.container}>
        <View style={styles.centerBox}>
          <MaterialIcons name="home" size={80} color="#2979ff" style={styles.icon} />
          <Text style={styles.title}>Chào mừng bạn trở lại!</Text>
          <Text style={styles.subtitle}>Hệ thống điểm danh FaceID</Text>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: height,
  },
  centerBox: {
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    paddingHorizontal: 24,
    paddingVertical: 40,
    backgroundColor: 'rgba(255,255,255,0.85)',
    borderRadius: 24,
    elevation: 4,
    shadowColor: '#2979ff',
    shadowOpacity: 0.09,
    shadowRadius: 12,
  },
  icon: {
    marginBottom: 18,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#2979ff",
    textAlign: "center",
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 18,
    color: "#222",
    textAlign: "center",
    fontWeight: "500",
  },
});
