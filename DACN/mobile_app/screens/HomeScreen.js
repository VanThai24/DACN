import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Dimensions, Image, ActivityIndicator, ScrollView, TouchableOpacity, Alert } from "react-native";
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import { LinearGradient } from "expo-linear-gradient";
import axios from "axios";
import { API_URL } from "../config";

const { height, width } = Dimensions.get('window');

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

export default function HomeScreen({ user, navigation }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
  }, [user]);

  const name = user?.full_name || user?.name || user?.username || "Nhân viên";
  const department = user?.department || user?.department_name || "Chưa cập nhật";
  let avatar = user?.avatar;
  if (!avatar) {
    avatar = user?.photo_path || user?.photoPath;
    if (avatar && avatar.startsWith("/")) {
      avatar = `http://${user?.server_ip || '192.168.110.45'}:8000${avatar}`;
    }
  }
  if (!avatar) avatar = "https://randomuser.me/api/portraits/men/32.jpg";

  const monthDays = getMonthStats(records);
  const { ontime, late } = getCheckinStats(records);
  const total = ontime + late;
  const ontimePercent = total > 0 ? Math.round((ontime / total) * 100) : 0;

  const QuickActionButton = ({ icon, label, color, onPress }) => (
    <TouchableOpacity style={[styles.quickAction, { borderColor: color }]} onPress={onPress}>
      <LinearGradient
        colors={[color + '15', color + '05']}
        style={styles.quickActionGradient}
      >
        <Ionicons name={icon} size={28} color={color} />
        <Text style={[styles.quickActionText, { color }]}>{label}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <LinearGradient colors={["#667eea", "#764ba2", "#f093fb"]} style={styles.gradient}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.container}>
          {/* Header Card with Wave Background */}
          <View style={styles.headerCard}>
            <LinearGradient colors={["#ffffff", "#f8f9fa"]} style={styles.headerGradient}>
              <View style={styles.headerContent}>
                <View style={styles.avatarContainer}>
                  <Image source={{ uri: avatar }} style={styles.avatar} />
                  <View style={styles.onlineBadge} />
                </View>
                <View style={styles.headerInfo}>
                  <Text style={styles.greeting}>Xin chào 👋</Text>
                  <Text style={styles.name}>{name}</Text>
                  <View style={styles.departmentBadge}>
                    <MaterialIcons name="business" size={14} color="#667eea" />
                    <Text style={styles.department}>{department}</Text>
                  </View>
                </View>
              </View>
            </LinearGradient>
          </View>

          {/* Quick Actions */}
          <View style={styles.quickActionsContainer}>
            <Text style={styles.sectionTitle}>Thao tác nhanh</Text>
            <View style={styles.quickActionsGrid}>
              <QuickActionButton 
                icon="calendar-outline" 
                label="Lịch sử" 
                color="#f093fb" 
                onPress={() => navigation.navigate('Attendance')} 
              />
              <QuickActionButton 
                icon="person-outline" 
                label="Hồ sơ" 
                color="#feca57" 
                onPress={() => navigation.navigate('Profile')} 
              />
              <QuickActionButton 
                icon="stats-chart" 
                label="Thống kê" 
                color="#00d4ff" 
                onPress={() => Alert.alert('Thống kê', 'Xem thống kê chi tiết tại trang Điểm danh')} 
              />
              <QuickActionButton 
                icon="information-circle" 
                label="Hỗ trợ" 
                color="#43a047" 
                onPress={() => Alert.alert('Hỗ trợ', 'Liên hệ IT: 0123456789')} 
              />
            </View>
          </View>

          {/* Stats Container with Modern Design */}
          <View style={styles.statsContainer}>
            <Text style={styles.sectionTitle}>📊 Thống kê tháng {new Date().getMonth() + 1}</Text>
            {loading ? (
              <ActivityIndicator size="large" color="#667eea" style={{ marginTop: 30 }} />
            ) : (
              <>
                {/* Main Stats Card */}
                <View style={styles.mainStatsCard}>
                  <LinearGradient colors={["#667eea", "#764ba2"]} style={styles.mainStatsGradient}>
                    <View style={styles.mainStatItem}>
                      <Text style={styles.mainStatNumber}>{monthDays}</Text>
                      <Text style={styles.mainStatLabel}>Ngày làm việc</Text>
                    </View>
                    <View style={styles.mainStatDivider} />
                    <View style={styles.mainStatItem}>
                      <Text style={styles.mainStatNumber}>{ontimePercent}%</Text>
                      <Text style={styles.mainStatLabel}>Đúng giờ</Text>
                    </View>
                  </LinearGradient>
                </View>

                {/* Detail Stats Grid */}
                <View style={styles.statsGrid}>
                  <View style={[styles.statCard, { borderLeftColor: "#43a047" }]}>
                    <View style={[styles.statIconCircle, { backgroundColor: "#43a04715" }]}>
                      <MaterialIcons name="check-circle" size={32} color="#43a047" />
                    </View>
                    <Text style={styles.statNumber}>{ontime}</Text>
                    <Text style={styles.statLabel}>Đúng giờ</Text>
                  </View>

                  <View style={[styles.statCard, { borderLeftColor: "#e53935" }]}>
                    <View style={[styles.statIconCircle, { backgroundColor: "#e5393515" }]}>
                      <MaterialIcons name="access-time" size={32} color="#e53935" />
                    </View>
                    <Text style={styles.statNumber}>{late}</Text>
                    <Text style={styles.statLabel}>Đi trễ</Text>
                  </View>
                </View>

                <View style={styles.statsGrid}>
                  <View style={[styles.statCard, { borderLeftColor: "#2979ff" }]}>
                    <View style={[styles.statIconCircle, { backgroundColor: "#2979ff15" }]}>
                      <MaterialIcons name="schedule" size={32} color="#2979ff" />
                    </View>
                    <Text style={styles.statNumber}>{total}</Text>
                    <Text style={styles.statLabel}>Tổng lần</Text>
                  </View>

                  <View style={[styles.statCard, { borderLeftColor: "#ffa726" }]}>
                    <View style={[styles.statIconCircle, { backgroundColor: "#ffa72615" }]}>
                      <MaterialIcons name="trending-up" size={32} color="#ffa726" />
                    </View>
                    <Text style={styles.statNumber}>{monthDays * 8}h</Text>
                    <Text style={styles.statLabel}>Thời gian</Text>
                  </View>
                </View>
              </>
            )}
          </View>

          {/* Info Banner */}
          <View style={styles.infoBanner}>
            <LinearGradient colors={["#667eea20", "#764ba220"]} style={styles.infoBannerGradient}>
              <Ionicons name="shield-checkmark" size={28} color="#667eea" />
              <View style={styles.infoTextContainer}>
                <Text style={styles.infoTitle}>Hệ thống FaceID</Text>
                <Text style={styles.infoSubtitle}>Điểm danh tự động và bảo mật</Text>
              </View>
            </LinearGradient>
          </View>

          <View style={{ height: 30 }} />
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  scrollView: { flex: 1 },
  container: {
    flex: 1,
    padding: 16,
  },
  headerCard: {
    marginTop: 10,
    marginBottom: 20,
    borderRadius: 24,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
  },
  headerGradient: {
    padding: 20,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 16,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: '#fff',
  },
  onlineBadge: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#43a047',
    borderWidth: 3,
    borderColor: '#fff',
  },
  headerInfo: {
    flex: 1,
  },
  greeting: {
    fontSize: 15,
    color: '#666',
    marginBottom: 4,
  },
  name: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  departmentBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#667eea15',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
  },
  department: {
    fontSize: 13,
    color: '#667eea',
    fontWeight: '600',
    marginLeft: 6,
  },

  // Quick Actions
  quickActionsContainer: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
    paddingLeft: 4,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: (width - 48) / 4,
    marginBottom: 12,
    borderRadius: 16,
    borderWidth: 2,
    overflow: 'hidden',
  },
  quickActionGradient: {
    padding: 12,
    alignItems: 'center',
  },
  quickActionText: {
    fontSize: 11,
    fontWeight: '600',
    marginTop: 6,
    textAlign: 'center',
  },

  // Stats Container
  statsContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  mainStatsCard: {
    marginTop: 16,
    marginBottom: 20,
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 4,
  },
  mainStatsGradient: {
    flexDirection: 'row',
    paddingVertical: 24,
    paddingHorizontal: 20,
  },
  mainStatItem: {
    flex: 1,
    alignItems: 'center',
  },
  mainStatNumber: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  mainStatLabel: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  mainStatDivider: {
    width: 1,
    backgroundColor: '#ffffff40',
    marginHorizontal: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    borderLeftWidth: 4,
    elevation: 2,
  },
  statIconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statNumber: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginVertical: 4,
  },
  statLabel: {
    fontSize: 13,
    color: '#666',
    textAlign: 'center',
    fontWeight: '500',
  },

  // Info Banner
  infoBanner: {
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 4,
  },
  infoBannerGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  infoTextContainer: {
    flex: 1,
    marginLeft: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 4,
  },
  infoSubtitle: {
    fontSize: 13,
    color: '#764ba2',
  },
});
