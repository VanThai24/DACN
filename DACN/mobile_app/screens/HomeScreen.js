import React, { useEffect, useState, useRef } from "react";
import { View, Text, StyleSheet, Dimensions, Image, ActivityIndicator, ScrollView, TouchableOpacity, Alert, Animated } from "react-native";
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import { LinearGradient } from "expo-linear-gradient";
import axios from "axios";
import { API_URL, SERVER_IP } from "../config";
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';
import { spacing } from '../theme/spacing';

const { height, width } = Dimensions.get('window');

// Đếm số ngày làm việc trong tháng
function getWorkdaysInMonth() {
  const now = new Date();
  const month = now.getMonth();
  const year = now.getFullYear();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  let workdays = 0;
  
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i);
    const dayOfWeek = date.getDay();
    if (dayOfWeek >= 1 && dayOfWeek <= 5) workdays++;
  }
  
  return workdays;
}

function getMonthStats(records) {
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const days = new Set();
  records.forEach(r => {
    const d = new Date(r.timestamp_in);
    if (d.getMonth() + 1 === month && d.getFullYear() === year) {
      days.add(d.toDateString());
    }
  });
  return days.size;
}

function getCheckinStats(records) {
  let ontime = 0, late = 0;
  records.forEach(r => {
    if (!r.timestamp_in) return;
    const d = new Date(r.timestamp_in);
    const hour = d.getHours();
    const minute = d.getMinutes();
    if (hour < 8 || (hour === 8 && minute <= 5)) ontime++;
    else late++;
  });
  return { ontime, late };
}

function getAbsentDays(records) {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const month = now.getMonth();
  const year = now.getFullYear();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  // Tạo Set các ngày đã điểm danh
  const attendedDays = new Set();
  records.forEach(r => {
    const d = new Date(r.timestamp_in);
    if (d.getMonth() === month && d.getFullYear() === year) {
      attendedDays.add(d.getDate());
    }
  });
  
  // Đếm số ngày vắng (chỉ tính ngày đã qua)
  let absentCount = 0;
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i);
    const dayOfWeek = date.getDay();
    // Chỉ tính ngày làm việc (thứ 2-6) và đã qua
    if (dayOfWeek >= 1 && dayOfWeek <= 5 && date < now) {
      if (!attendedDays.has(i)) {
        absentCount++;
      }
    }
  }
  
  return absentCount;
}

// Tính tổng số giờ làm việc thực tế trong tháng
function getTotalWorkHours(records) {
  const now = new Date();
  const month = now.getMonth();
  const year = now.getFullYear();
  let totalHours = 0;
  
  records.forEach(r => {
    const d = new Date(r.timestamp_in);
    if (d.getMonth() === month && d.getFullYear() === year) {
      // Nếu có timestamp_out, tính giờ làm thực tế
      if (r.timestamp_out) {
        const timeIn = new Date(r.timestamp_in);
        const timeOut = new Date(r.timestamp_out);
        const diffMs = timeOut - timeIn;
        const hours = diffMs / (1000 * 60 * 60);
        totalHours += hours;
      } else {
        // Nếu chưa checkout, giả định làm 8 giờ
        totalHours += 8;
      }
    }
  });
  
  return Math.round(totalHours);
}

export default function HomeScreen({ user, navigation }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

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
      })
    ]).start();
  }, []);

  const fetchAttendance = () => {
    if (!user?.employee_id) {
      console.log('No employee_id in user:', user);
      return;
    }
    console.log('Fetching attendance for employee_id:', user.employee_id);
    setLoading(true);
    axios.get(`${API_URL}/attendance/employee/${user.employee_id}`)
      .then(res => {
        console.log('HomeScreen attendance data:', res.data);
        setRecords(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('HomeScreen fetch error:', err);
        setRecords([]);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAttendance();
    // Auto refresh mỗi 5 phút
    const interval = setInterval(() => {
      fetchAttendance();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [user]);

  const name = user?.full_name || user?.name || user?.username || "Nhân viên";
  const department = user?.department || user?.department_name || "Chưa cập nhật";
  
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
    const initial = name.charAt(0).toUpperCase();
    avatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=3b82f6&color=fff&size=200`;
  }
  
  console.log('HomeScreen - Avatar:', { 
    username: user?.username,
    user_avatar: user?.avatar,
    photo_path: user?.photo_path,
    final_avatar: avatar 
  });

  const monthDays = getMonthStats(records);
  const { ontime, late } = getCheckinStats(records);
  const absentDays = getAbsentDays(records);
  const totalWorkdays = getWorkdaysInMonth();
  const totalWorkHours = getTotalWorkHours(records);
  const total = ontime + late;
  const ontimePercent = total > 0 ? Math.round((ontime / total) * 100) : 0;

  // Removed QuickActionButton component - using inline TouchableOpacity instead

  return (
    <View style={styles.gradient}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Animated.View style={[styles.container, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.avatarContainer}>
              <Image 
                source={{ uri: avatar }} 
                style={styles.avatar}
                onError={(e) => console.log('Avatar load error:', e.nativeEvent.error)}
                onLoad={() => console.log('Avatar loaded successfully:', avatar)}
              />
            </View>
            <Text style={styles.name}>{name}</Text>
            <View style={styles.departmentBadge}>
              <MaterialIcons name="business" size={14} color="#64748b" />
              <Text style={styles.department}>{department}</Text>
            </View>
          </View>

          {/* Quick Actions */}
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Attendance')}>
              <View style={[styles.quickActionIcon, { backgroundColor: '#e0f2fe' }]}>
                <Ionicons name="calendar" size={24} color="#3b82f6" />
              </View>
              <Text style={styles.quickActionText}>Lịch sử</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Profile')}>
              <View style={[styles.quickActionIcon, { backgroundColor: '#f3e8ff' }]}>
                <Ionicons name="person" size={24} color="#8b5cf6" />
              </View>
              <Text style={styles.quickActionText}>Hồ sơ</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction} onPress={() => Alert.alert('Thống kê', 'Xem thống kê chi tiết tại trang Điểm danh')}>
              <View style={[styles.quickActionIcon, { backgroundColor: '#fce7f3' }]}>
                <Ionicons name="stats-chart" size={24} color="#ec4899" />
              </View>
              <Text style={styles.quickActionText}>Thống kê</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.quickAction} onPress={() => Alert.alert('Hỗ trợ', 'Liên hệ IT: 0123456789')}>
              <View style={[styles.quickActionIcon, { backgroundColor: '#d1fae5' }]}>
                <Ionicons name="help-circle" size={24} color="#10b981" />
              </View>
              <Text style={styles.quickActionText}>Hỗ trợ</Text>
            </TouchableOpacity>
          </View>

          {/* Stats Section */}
          <View style={styles.statsSection}>
            <Text style={styles.sectionTitle}>Thống kê tháng {new Date().getMonth() + 1}</Text>
            {loading ? (
              <ActivityIndicator size="large" color="#3b82f6" style={{ marginTop: 30 }} />
            ) : (
              <>
                {/* Main Stats */}
                <View style={styles.mainStatsRow}>
                  <View style={styles.mainStatCard}>
                    <Text style={styles.mainStatNumber}>{monthDays}</Text>
                    <Text style={styles.mainStatLabel}>Ngày làm việc</Text>
                  </View>
                  <View style={styles.mainStatCard}>
                    <Text style={styles.mainStatNumber}>{ontimePercent}%</Text>
                    <Text style={styles.mainStatLabel}>Đúng giờ</Text>
                  </View>
                </View>

                {/* Detail Stats */}
                <View style={styles.detailStatsGrid}>
                  <View style={styles.detailStatCard}>
                    <MaterialIcons name="check-circle" size={20} color="#10b981" />
                    <Text style={styles.detailStatNumber}>{ontime}</Text>
                    <Text style={styles.detailStatLabel}>Đúng giờ</Text>
                  </View>
                  <View style={styles.detailStatCard}>
                    <MaterialIcons name="access-time" size={20} color="#ef4444" />
                    <Text style={styles.detailStatNumber}>{late}</Text>
                    <Text style={styles.detailStatLabel}>Đi trễ</Text>
                  </View>
                  <View style={styles.detailStatCard}>
                    <MaterialIcons name="event-busy" size={20} color="#f59e0b" />
                    <Text style={styles.detailStatNumber}>{absentDays}</Text>
                    <Text style={styles.detailStatLabel}>Vắng</Text>
                  </View>
                  <View style={styles.detailStatCard}>
                    <MaterialIcons name="schedule" size={20} color="#64748b" />
                    <Text style={styles.detailStatNumber}>{totalWorkHours}h</Text>
                    <Text style={styles.detailStatLabel}>Tổng giờ</Text>
                  </View>
                </View>
              </>
            )}
          </View>

          <View style={{ height: 20 }} />
        </Animated.View>
      </ScrollView>
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
    padding: 20,
  },
  header: {
    marginBottom: 24,
    alignItems: 'center',
  },
  avatarContainer: {
    marginBottom: 12,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
    textAlign: 'center',
  },
  departmentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  department: {
    fontSize: 13,
    color: '#64748b',
    fontWeight: '500',
    marginLeft: 6,
  },

  quickActionsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  quickAction: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
    marginHorizontal: 4,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  quickActionText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#334155',
  },

  // Stats Section
  statsSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 16,
  },
  mainStatsRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  mainStatCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
    marginHorizontal: 4,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  mainStatNumber: {
    fontSize: 36,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
  },
  mainStatLabel: {
    fontSize: 14,
    color: '#64748b',
    fontWeight: '500',
  },
  detailStatsGrid: {
    flexDirection: 'row',
  },
  detailStatCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
    marginHorizontal: 4,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  detailStatNumber: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
  },
  detailStatLabel: {
    fontSize: 11,
    color: '#64748b',
    textAlign: 'center',
  },
});
