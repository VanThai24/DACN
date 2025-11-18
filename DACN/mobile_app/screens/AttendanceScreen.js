import React, { useEffect, useState, useRef } from "react";
import { View, Text, FlatList, StyleSheet, RefreshControl, TouchableOpacity, Modal, ScrollView, Animated } from "react-native";
import axios from "axios";
import { MaterialIcons } from '@expo/vector-icons';
import { LinearGradient } from "expo-linear-gradient";
import { API_URL } from "../config";
import { colors } from '../theme/colors';
import { typography } from '../theme/typography';
import { spacing } from '../theme/spacing';

// Tạo danh sách tất cả ngày làm việc trong tháng
function getAllWorkdaysInMonth() {
  const now = new Date();
  const month = now.getMonth();
  const year = now.getFullYear();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const workdays = [];
  
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i);
    const dayOfWeek = date.getDay();
    // Thứ 2-6 (1-5) là ngày làm việc
    if (dayOfWeek >= 1 && dayOfWeek <= 5) {
      workdays.push(date);
    }
  }
  
  return workdays;
}

// Merge dữ liệu thực tế với tất cả ngày làm việc
function mergeAttendanceWithWorkdays(records) {
  const workdays = getAllWorkdaysInMonth();
  const now = new Date();
  now.setHours(0, 0, 0, 0); // Reset time để so sánh ngày
  
  // Tạo map từ records hiện có (bao gồm cả records ngoài giờ làm việc)
  const recordMap = new Map();
  const allRecords = []; // Lưu tất cả records thực tế
  
  records.forEach(r => {
    if (r.timestamp_in) {
      const d = new Date(r.timestamp_in);
      const dateKey = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
      recordMap.set(dateKey, r);
      allRecords.push(r);
    }
  });
  
  // Tạo danh sách ngày làm việc với trạng thái vắng/tương lai
  const workdayList = workdays.map(workday => {
    const dateKey = `${workday.getFullYear()}-${workday.getMonth()}-${workday.getDate()}`;
    const existingRecord = recordMap.get(dateKey);
    
    if (existingRecord) {
      recordMap.delete(dateKey); // Xóa để không bị trùng
      return existingRecord;
    } else if (workday <= now) {
      // Ngày đã qua hoặc hôm nay mà không có dữ liệu = VẮNG
      return {
        id: `absent-${dateKey}`,
        timestamp_in: workday.toISOString(),
        status: 'absent',
        isAbsent: true
      };
    } else {
      // Ngày chưa đến (tương lai)
      return {
        id: `future-${dateKey}`,
        timestamp_in: workday.toISOString(),
        status: 'future',
        isFuture: true
      };
    }
  });
  
  // Thêm các records còn lại (thứ 7/CN - làm ngoài giờ)
  const weekendRecords = Array.from(recordMap.values());
  const fullList = [...workdayList, ...weekendRecords];
  
  // Sắp xếp theo ngày, mới nhất trước
  fullList.sort((a, b) => new Date(b.timestamp_in) - new Date(a.timestamp_in));
  
  return fullList;
}

function getMonthStats(records) {
  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const days = new Set();
  records.forEach(r => {
    if (r.isAbsent || r.isFuture) return; // Bỏ qua ngày vắng và ngày tương lai
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
    if (r.isAbsent || r.isFuture) return;
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
    if (r.isAbsent || r.isFuture || !r.timestamp_in) return;
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
  return records.filter(r => r.isAbsent).length;
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
  const [fullRecords, setFullRecords] = useState([]); // Bao gồm cả ngày vắng
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(30)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 500,
        useNativeDriver: true,
      })
    ]).start();
  }, []);

  const fetchRecords = () => {
    if (!user?.employee_id) {
      console.log('No employee_id found for user:', user);
      return;
    }
    console.log('Fetching attendance for employee_id:', user.employee_id);
    axios.get(`${API_URL}/attendance/employee/${user.employee_id}`)
      .then(res => {
        console.log('Attendance data received:', res.data);
        setRecords(res.data);
        // Merge với tất cả ngày làm việc
        const merged = mergeAttendanceWithWorkdays(res.data);
        setFullRecords(merged);
      })
      .catch(err => {
        console.error('Fetch attendance error:', err);
        setRecords([]);
        // Vẫn hiển thị ngày vắng nếu API fail
        const merged = mergeAttendanceWithWorkdays([]);
        setFullRecords(merged);
      });
  };

  useEffect(() => {
    fetchRecords();
    // Auto refresh mỗi 5 phút để cập nhật real-time
    const interval = setInterval(() => {
      fetchRecords();
    }, 5 * 60 * 1000); // 5 minutes
    
    return () => clearInterval(interval);
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
    <View style={styles.gradient}>
      <Animated.View style={[styles.container, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
        <View style={styles.header}>
          <Text style={styles.title}>Lịch sử điểm danh</Text>
          <Text style={styles.subtitle}>Tháng {new Date().getMonth() + 1}/{new Date().getFullYear()}</Text>
        </View>

        {/* Stats Cards Grid */}
        <View style={styles.statsContainer}>
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <View style={[styles.statIconCircle, { backgroundColor: '#dbeafe' }]}>
                <MaterialIcons name="event-available" size={24} color="#3b82f6" />
              </View>
              <Text style={styles.statNumber}>{monthDays}</Text>
              <Text style={styles.statLabel}>Tháng này</Text>
            </View>
            <View style={styles.statCard}>
              <View style={[styles.statIconCircle, { backgroundColor: '#d1fae5' }]}>
                <MaterialIcons name="check-circle" size={24} color="#10b981" />
              </View>
              <Text style={styles.statNumber}>{ontime}</Text>
              <Text style={styles.statLabel}>Đúng giờ</Text>
            </View>
          </View>
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <View style={[styles.statIconCircle, { backgroundColor: '#fee2e2' }]}>
                <MaterialIcons name="access-time" size={24} color="#ef4444" />
              </View>
              <Text style={styles.statNumber}>{late}</Text>
              <Text style={styles.statLabel}>Trễ giờ</Text>
            </View>
            <View style={styles.statCard}>
              <View style={[styles.statIconCircle, { backgroundColor: '#fef3c7' }]}>
                <MaterialIcons name="event" size={24} color="#f59e0b" />
              </View>
              <Text style={styles.statNumber}>{quarterDays}</Text>
              <Text style={styles.statLabel}>Quý này</Text>
            </View>
          </View>
        </View>

        {/* Records List */}
        <View style={styles.listContainer}>
          <Text style={styles.listTitle}>Chi tiết điểm danh ({fullRecords.length} ngày)</Text>
          <FlatList
            data={fullRecords}
            keyExtractor={item => item.id.toString()}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={["#667eea"]} />
            }
            renderItem={({ item }) => {
              // Xử lý hiển thị cho các trạng thái khác nhau
              let statusBadgeStyle, statusText, statusIcon, isLate = false;
              
              if (item.isAbsent) {
                statusBadgeStyle = styles.absentBadge;
                statusText = "✗ Vắng";
                statusIcon = "event-busy";
              } else if (item.isFuture) {
                statusBadgeStyle = styles.futureBadge;
                statusText = "○ Chưa đến";
                statusIcon = "schedule";
              } else {
                // Tính toán trễ/đúng giờ dựa vào start_time và timestamp_in
                if (item.start_time && item.timestamp_in) {
                  const [startHour, startMin] = item.start_time.split(':').map(Number);
                  const checkinTime = new Date(item.timestamp_in);
                  const checkinHour = checkinTime.getHours();
                  const checkinMin = checkinTime.getMinutes();
                  
                  // So sánh: Trễ nếu checkin sau start_time + 5 phút
                  const startTotalMin = startHour * 60 + startMin;
                  const checkinTotalMin = checkinHour * 60 + checkinMin;
                  const lateMins = checkinTotalMin - startTotalMin;
                  
                  if (lateMins > 5) {
                    isLate = true;
                    statusBadgeStyle = styles.lateBadge;
                    statusText = `⚠ Trễ ${lateMins} phút`;
                    statusIcon = "warning";
                  } else {
                    statusBadgeStyle = styles.presentBadge;
                    statusText = "✓ Đúng giờ";
                    statusIcon = "check-circle";
                  }
                } else {
                  // Fallback nếu không có start_time
                  statusBadgeStyle = styles.presentBadge;
                  statusText = "✓ Có mặt";
                  statusIcon = "check-circle";
                }
              }
              
              return (
                <TouchableOpacity 
                  style={[styles.card, item.isAbsent && styles.absentCard, item.isFuture && styles.futureCard]}
                  onPress={() => {
                    if (!item.isFuture) {
                      setSelectedRecord(item);
                      setModalVisible(true);
                    }
                  }}
                  disabled={item.isFuture}
                >
                  <View style={styles.cardHeader}>
                    <View style={styles.cardDateBadge}>
                      <MaterialIcons name={item.isFuture ? "schedule" : "calendar-today"} size={18} color={item.isFuture ? "#999" : "#667eea"} />
                      <Text style={[styles.cardDate, item.isFuture && styles.futureText]}>{formatDateTime(item.timestamp_in).split(' ')[0]}</Text>
                      {item.is_overtime && (
                        <View style={styles.overtimeBadge}>
                          <Text style={styles.overtimeText}>Tăng ca</Text>
                        </View>
                      )}
                    </View>
                    <View style={[styles.statusBadge, statusBadgeStyle]}>
                      <MaterialIcons name={statusIcon} size={16} color="#fff" style={{marginRight: 4}} />
                      <Text style={styles.statusText}>{statusText}</Text>
                    </View>
                  </View>
                  <View style={styles.cardBody}>
                    {item.isAbsent ? (
                      <View style={styles.absentInfo}>
                        <MaterialIcons name="cancel" size={40} color="#e53935" />
                        <Text style={styles.absentText}>Không có dữ liệu điểm danh</Text>
                      </View>
                    ) : item.isFuture ? (
                      <View style={styles.futureInfo}>
                        <MaterialIcons name="schedule" size={40} color="#999" />
                        <Text style={styles.futureInfoText}>Ngày chưa đến</Text>
                      </View>
                    ) : (
                      <View style={styles.timeRow}>
                        <View style={styles.timeItem}>
                          <MaterialIcons name="login" size={24} color="#43a047" />
                          <Text style={styles.timeLabel}>Ca làm</Text>
                          <Text style={styles.timeValue}>
                            {item.start_time && item.end_time 
                              ? `${item.start_time} - ${item.end_time}`
                              : formatDateTime(item.timestamp_in).split(' ')[1]
                            }
                          </Text>
                        </View>
                        <View style={styles.timeDivider} />
                        <View style={styles.timeItem}>
                          <MaterialIcons name="schedule" size={24} color="#2979ff" />
                          <Text style={styles.timeLabel}>Điểm danh</Text>
                          <Text style={styles.timeValue}>
                            {item.timestamp_in ? formatDateTime(item.timestamp_in).split(' ')[1] : "-"}
                          </Text>
                        </View>
                      </View>
                    )}
                  </View>
                </TouchableOpacity>
              );
            }}
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
                      <MaterialIcons name="access-time" size={24} color="#43a047" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Ca làm việc</Text>
                        <Text style={styles.detailValue}>
                          {selectedRecord.start_time && selectedRecord.end_time 
                            ? `${selectedRecord.start_time} - ${selectedRecord.end_time}`
                            : "Chưa có thông tin ca"
                          }
                        </Text>
                      </View>
                    </View>
                    <View style={styles.detailRow}>
                      <MaterialIcons name="login" size={24} color="#2979ff" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Thời gian điểm danh</Text>
                        <Text style={styles.detailValue}>
                          {selectedRecord.timestamp_in ? formatDateTime(selectedRecord.timestamp_in) : "-"}
                        </Text>
                      </View>
                    </View>
                    {selectedRecord.start_time && selectedRecord.timestamp_in && (() => {
                      const [startHour, startMin] = selectedRecord.start_time.split(':').map(Number);
                      const checkinTime = new Date(selectedRecord.timestamp_in);
                      const checkinHour = checkinTime.getHours();
                      const checkinMin = checkinTime.getMinutes();
                      const startTotalMin = startHour * 60 + startMin;
                      const checkinTotalMin = checkinHour * 60 + checkinMin;
                      const lateMins = checkinTotalMin - startTotalMin;
                      
                      return lateMins > 5 ? (
                        <View style={styles.detailRow}>
                          <MaterialIcons name="warning" size={24} color="#f57c00" />
                          <View style={styles.detailText}>
                            <Text style={styles.detailLabel}>Trạng thái</Text>
                            <Text style={[styles.detailValue, {color: '#f57c00', fontWeight: '600'}]}>
                              Trễ {lateMins} phút
                            </Text>
                          </View>
                        </View>
                      ) : (
                        <View style={styles.detailRow}>
                          <MaterialIcons name="check-circle" size={24} color="#43a047" />
                          <View style={styles.detailText}>
                            <Text style={styles.detailLabel}>Trạng thái</Text>
                            <Text style={[styles.detailValue, {color: '#43a047', fontWeight: '600'}]}>
                              Đúng giờ
                            </Text>
                          </View>
                        </View>
                      );
                    })()}
                    <View style={styles.detailRow}>
                      <MaterialIcons name="devices" size={24} color="#ffa726" />
                      <View style={styles.detailText}>
                        <Text style={styles.detailLabel}>Thiết bị</Text>
                        <Text style={styles.detailValue}>{selectedRecord.device_id || "N/A"}</Text>
                      </View>
                    </View>
                    {selectedRecord.is_overtime && (
                      <View style={styles.detailRow}>
                        <MaterialIcons name="alarm-on" size={24} color="#ff6f00" />
                        <View style={styles.detailText}>
                          <Text style={styles.detailLabel}>Loại ca</Text>
                          <Text style={[styles.detailValue, {color: '#ff6f00', fontWeight: '600'}]}>Tăng ca</Text>
                        </View>
                      </View>
                    )}
                    {selectedRecord.overtime_note && (
                      <View style={styles.detailRow}>
                        <MaterialIcons name="note" size={24} color="#757575" />
                        <View style={styles.detailText}>
                          <Text style={styles.detailLabel}>Ghi chú tăng ca</Text>
                          <Text style={styles.detailValue}>{selectedRecord.overtime_note}</Text>
                        </View>
                      </View>
                    )}
                  </>
                )}
              </ScrollView>
            </View>
          </View>
        </Modal>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  gradient: { 
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  container: { 
    flex: 1, 
    padding: 16,
  },
  header: {
    marginBottom: 20,
    marginTop: 8,
  },
  title: { 
    fontSize: 24, 
    fontWeight: '700', 
    color: '#0f172a', 
    textAlign: "center",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#64748b',
    textAlign: "center",
    fontWeight: typography.weights.medium,
  },
  
  // Stats Container
  statsContainer: {
    marginBottom: spacing.md,
  },
  statsRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
  },
  statNumber: {
    fontSize: 28,
    fontWeight: '700',
    color: '#0f172a',
    marginVertical: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '500',
  },

  // List Container
  listContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 16,
  },

  // Card Styles
  card: { 
    backgroundColor: '#fff', 
    borderRadius: 12, 
    padding: 16, 
    marginBottom: 12, 
    borderLeftWidth: 3, 
    borderLeftColor: '#3b82f6', 
    borderColor: '#e2e8f0', 
    elevation: 2, 
    shadowColor: '#000', 
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08, 
    shadowRadius: 3,
  },
  statIconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  cardDateBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e0f2fe',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    gap: 6,
  },
  cardDate: {
    fontSize: 13,
    fontWeight: '700',
    color: '#3b82f6',
    marginLeft: 4,
  },
  overtimeBadge: {
    backgroundColor: '#fff3e0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#ff6f00',
  },
  overtimeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#ff6f00',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  presentBadge: {
    backgroundColor: '#10b981',
  },
  lateBadge: {
    backgroundColor: '#f59e0b',
  },
  absentBadge: {
    backgroundColor: '#ef4444',
  },
  futureBadge: {
    backgroundColor: '#94a3b8',
  },
  statusText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#fff',
  },
  
  // Absent & Future Card Styles
  absentCard: {
    borderLeftColor: '#ef4444',
    backgroundColor: '#fef2f2',
  },
  futureCard: {
    borderLeftColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
    opacity: 0.75,
  },
  absentInfo: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  absentText: {
    fontSize: typography.sizes.sm,
    color: colors.error.main,
    fontWeight: typography.weights.bold,
    marginTop: spacing.sm,
  },
  futureInfo: {
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  futureInfoText: {
    fontSize: typography.sizes.sm,
    color: colors.text.secondary,
    marginTop: spacing.sm,
    fontWeight: typography.weights.medium,
  },
  futureText: {
    color: colors.text.secondary,
  },

  // Card Body
  cardBody: {
    marginTop: spacing.sm,
  },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timeItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: spacing.xs,
  },
  timeLabel: {
    fontSize: typography.sizes.xs,
    color: colors.text.secondary,
    marginTop: spacing.sm,
    fontWeight: typography.weights.semibold,
  },
  timeValue: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
    marginTop: spacing.xs,
  },
  timeDivider: {
    width: 2,
    height: 70,
    backgroundColor: colors.gray[200],
    marginHorizontal: spacing.md,
    borderRadius: spacing.borderRadius.sm,
  },

  // Empty State
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.xxl * 2,
  },
  empty: { 
    textAlign: "center", 
    color: colors.text.secondary, 
    fontSize: typography.sizes.md, 
    marginTop: spacing.md,
    fontWeight: typography.weights.medium,
  },

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: colors.white,
    borderTopLeftRadius: spacing.borderRadius.xl,
    borderTopRightRadius: spacing.borderRadius.xl,
    padding: spacing.xl,
    maxHeight: '75%',
    elevation: 20,
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
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.gray[50],
    borderRadius: spacing.borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary.main,
  },
  detailText: {
    marginLeft: spacing.md,
    flex: 1,
  },
  detailLabel: {
    fontSize: typography.sizes.xs,
    color: colors.text.secondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    fontWeight: typography.weights.semibold,
    letterSpacing: 0.5,
  },
  detailValue: {
    fontSize: typography.sizes.md,
    color: colors.text.primary,
    fontWeight: typography.weights.bold,
  },
  in: {
    color: colors.success.main,
  },
  out: {
    color: colors.error.main,
  },
});
