import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet, RefreshControl, TouchableOpacity, Modal, ScrollView } from "react-native";
import axios from "axios";
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from "expo-linear-gradient";
import { API_URL } from "../config";

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

function getQuarterStats(records) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const quarter = Math.floor((month - 1) / 3) + 1;
  const days = new Set();
  records.forEach(r => {
    const d = new Date(r.timestamp_in);
    const m = d.getMonth() + 1;
    const q = Math.floor((m - 1) / 3) + 1;
    if (d.getFullYear() === year && q === quarter) {
      days.add(d.toDateString());
    }
  });
  return days.size;
}

function getCheckinStats(records) {
  let ontime = 0, late = 0;
  const checkedDays = new Set();
  records.forEach(r => {
    if (!r.timestamp_in) return;
    const d = new Date(r.timestamp_in);
    const hour = d.getHours();
    const minute = d.getMinutes();
    // Giả sử đúng giờ là trước 8:05
    if (hour < 8 || (hour === 8 && minute <= 5)) ontime++;
    else late++;
    checkedDays.add(d.toDateString());
  });
  return { ontime, late, checkedDays };
}

function getAbsentStats(records) {
  // Giả sử tháng hiện tại có 22 ngày làm việc
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const daysInMonth = new Date(year, month, 0).getDate();
  let workdays = 0;
  for (let i = 1; i <= daysInMonth; i++) {
    const d = new Date(year, month - 1, i);
    // Chỉ tính thứ 2-6
    if (d.getDay() >= 1 && d.getDay() <= 5) workdays++;
  }
  const { checkedDays } = getCheckinStats(records);
  return workdays - checkedDays.size;
}


function formatDateTime(timestamp) {
  if (!timestamp) return "-";
  const d = new Date(timestamp);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  return `${day}/${month}/${year} ${hour}:${minute}`;
}

export default function AttendanceScreen({ user }) {
  const [records, setRecords] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const fetchRecords = () => {
    if (!user?.id) return;
    axios.get(`${API_URL}/attendance/employee/${user.id}`)
      .then(res => setRecords(res.data))
      .catch(() => setRecords([]));
  };

  useEffect(() => {
    fetchRecords();
  }, [user]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchRecords();
    setTimeout(() => setRefreshing(false), 1000);
  };

  const monthDays = getMonthStats(records);
  const quarterDays = getQuarterStats(records);
  const { ontime, late } = getCheckinStats(records);
  const absent = getAbsentStats(records);

  return (
    <LinearGradient colors={["#667eea", "#764ba2"]} style={styles.gradient}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>📅 Lịch sử điểm danh</Text>
          <Text style={styles.subtitle}>Tháng {new Date().getMonth() + 1}/{new Date().getFullYear()}</Text>
        </View>

        {/* Stats Cards Grid */}
        <View style={styles.statsContainer}>
          <View style={styles.statsRow}>
            <View style={[styles.statCard, { backgroundColor: '#43a047' }]}>
              <MaterialIcons name="event-available" size={32} color="#fff" />
              <Text style={styles.statNumber}>{monthDays}</Text>
              <Text style={styles.statLabel}>Tháng này</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#2979ff' }]}>
              <MaterialIcons name="check-circle" size={32} color="#fff" />
              <Text style={styles.statNumber}>{ontime}</Text>
              <Text style={styles.statLabel}>Đúng giờ</Text>
            </View>
          </View>
          <View style={styles.statsRow}>
            <View style={[styles.statCard, { backgroundColor: '#e53935' }]}>
              <MaterialIcons name="access-time" size={32} color="#fff" />
              <Text style={styles.statNumber}>{late}</Text>
              <Text style={styles.statLabel}>Trễ giờ</Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: '#ffa726' }]}>
              <MaterialIcons name="event" size={32} color="#fff" />
              <Text style={styles.statNumber}>{quarterDays}</Text>
              <Text style={styles.statLabel}>Quý này</Text>
            </View>
          </View>
        </View>

        {/* Records List */}
        <View style={styles.listContainer}>
          <Text style={styles.listTitle}>Chi tiết điểm danh</Text>
          <FlatList
            data={records}
            keyExtractor={item => item.id.toString()}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#667eea"]} />
            }
            renderItem={({ item }) => (
              <TouchableOpacity 
                style={styles.card}
                onPress={() => {
                  setSelectedRecord(item);
                  setModalVisible(true);
                }}
              >
                <View style={styles.cardHeader}>
                  <View style={styles.cardDateBadge}>
                    <MaterialIcons name="calendar-today" size={18} color="#667eea" />
                    <Text style={styles.cardDate}>{formatDateTime(item.timestamp_in).split(' ')[0]}</Text>
                  </View>
                  <View style={[styles.statusBadge, item.status === "present" ? styles.presentBadge : styles.lateBadge]}>
                    <Text style={styles.statusText}>{item.status === "present" ? "✓ Có mặt" : "⚠ Trễ"}</Text>
                  </View>
                </View>
                <View style={styles.cardBody}>
                  <View style={styles.timeRow}>
                    <View style={styles.timeItem}>
                      <MaterialIcons name="login" size={24} color="#43a047" />
                      <Text style={styles.timeLabel}>Giờ vào</Text>
                      <Text style={styles.timeValue}>{formatDateTime(item.timestamp_in).split(' ')[1]}</Text>
                    </View>
                    <View style={styles.timeDivider} />
                    <View style={styles.timeItem}>
                      <MaterialIcons name="logout" size={24} color="#e53935" />
                      <Text style={styles.timeLabel}>Giờ ra</Text>
                      <Text style={styles.timeValue}>{item.timestamp_out ? formatDateTime(item.timestamp_out).split(' ')[1] : "-"}</Text>
                    </View>
                  </View>
                </View>
              </TouchableOpacity>
            )}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <MaterialIcons name="event-busy" size={80} color="#cccccc" />
                <Text style={styles.empty}>Chưa có dữ liệu điểm danh</Text>
              </View>
            }
          />
        </View>

        <Modal
          animationType="slide"
          transparent={true}
          visible={modalVisible}
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Chi tiết điểm danh</Text>
                <TouchableOpacity onPress={() => setModalVisible(false)}>
                  <MaterialIcons name="close" size={28} color="#666" />
                </TouchableOpacity>
              </View>
              <ScrollView>
                {selectedRecord && (
                  <>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="event" size={24} color="#2979ff" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Ngày</Text>
                        <Text style={styles.detailValue}>{formatDateTime(selectedRecord.timestamp_in).split(' ')[0]}</Text>
                      </View>
                    </View>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="login" size={24} color="#43a047" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Thời gian vào</Text>
                        <Text style={styles.detailValue}>{formatDateTime(selectedRecord.timestamp_in)}</Text>
                      </View>
                    </View>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="logout" size={24} color="#e53935" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Thời gian ra</Text>
                        <Text style={styles.detailValue}>{formatDateTime(selectedRecord.timestamp_out)}</Text>
                      </View>
                    </View>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="info" size={24} color="#2979ff" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Trạng thái</Text>
                        <Text style={[styles.detailValue, selectedRecord.status === "in" ? styles.in : styles.out]}>
                          {selectedRecord.status}
                        </Text>
                      </View>
                    </View>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="devices" size={24} color="#ffa726" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Thiết bị</Text>
                        <Text style={styles.detailValue}>{selectedRecord.device_id || "N/A"}</Text>
                      </View>
                    </View>
                  </>
                )}
              </ScrollView>
            </View>
          </View>
        </Modal>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  container: { flex: 1, padding: 16 },
  header: {
    marginBottom: 20,
    marginTop: 10,
  },
  title: { 
    fontSize: 28, 
    fontWeight: "bold", 
    color: "#fff", 
    textAlign: "center",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: "#ffffff90",
    textAlign: "center",
  },
  
  // Stats Container
  statsContainer: {
    marginBottom: 16,
  },
  statsRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statCard: {
    flex: 1,
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginVertical: 8,
  },
  statLabel: {
    fontSize: 13,
    color: '#fff',
    opacity: 0.9,
  },

  // List Container
  listContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 16,
    elevation: 8,
  },
  listTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 16,
  },

  // Card Styles
  card: { 
    backgroundColor: "#fff", 
    borderRadius: 16, 
    padding: 16, 
    marginBottom: 12, 
    borderWidth: 2, 
    borderColor: "#f0f0f0", 
    elevation: 2, 
    shadowColor: '#667eea', 
    shadowOpacity: 0.1, 
    shadowRadius: 8,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  cardDateBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#667eea15',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  cardDate: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#667eea',
    marginLeft: 6,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  presentBadge: {
    backgroundColor: '#43a04715',
  },
  lateBadge: {
    backgroundColor: '#e5393515',
  },
  statusText: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#43a047',
  },

  // Card Body
  cardBody: {
    marginTop: 8,
  },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeItem: {
    flex: 1,
    alignItems: 'center',
  },
  timeLabel: {
    fontSize: 13,
    color: '#666',
    marginTop: 8,
  },
  timeValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginTop: 4,
  },
  timeDivider: {
    width: 1,
    height: 60,
    backgroundColor: '#e0e0e0',
    marginHorizontal: 16,
  },

  // Empty State
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 80,
  },
  empty: { 
    textAlign: "center", 
    color: "#999", 
    fontSize: 16, 
    marginTop: 16,
  },

  // Modal Styles (keep existing)
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '70%',
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
    fontSize: 22,
    fontWeight: 'bold',
    color: '#2979ff',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  detailText: {
    marginLeft: 16,
    flex: 1,
  },
  detailLabel: {
    fontSize: 13,
    color: '#666',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    color: '#222',
    fontWeight: '600',
  },
});
