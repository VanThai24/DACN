import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
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


export default function AttendanceScreen({ user }) {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    if (!user?.id) return;
    axios.get(`${API_URL}/attendance/employee/${user.id}`)
      .then(res => setRecords(res.data))
      .catch(() => setRecords([]));
  }, [user]);

  const monthDays = getMonthStats(records);
  const quarterDays = getQuarterStats(records);
  const { ontime, late } = getCheckinStats(records);
  const absent = getAbsentStats(records);

  return (
    <LinearGradient colors={["#e3f0ff", "#f6f6f6"]} style={styles.gradient}>
      <View style={styles.container}>
        <Text style={styles.title}>Lịch sử điểm danh</Text>
        <View style={styles.statsBox}>
          <View style={styles.statsRow}>
            <MaterialIcons name="event-available" size={28} color="#43a047" />
            <Text style={styles.statsText}>Ngày điểm danh trong tháng: <Text style={styles.statsNum}>{monthDays}</Text></Text>
          </View>
          <View style={styles.statsRow}>
            <MaterialIcons name="event" size={28} color="#2979ff" />
            <Text style={styles.statsText}>Ngày điểm danh trong quý: <Text style={styles.statsNum}>{quarterDays}</Text></Text>
          </View>
          <View style={styles.statsRow}>
            <MaterialIcons name="check-circle" size={28} color="#2979ff" />
            <Text style={styles.statsText}>Điểm danh đúng giờ: <Text style={styles.statsNum}>{ontime}</Text></Text>
          </View>
          <View style={styles.statsRow}>
            <MaterialIcons name="error" size={28} color="#e53935" />
            <Text style={styles.statsText}>Điểm danh trễ: <Text style={styles.statsNum}>{late}</Text></Text>
          </View>
          <View style={styles.statsRow}>
            <MaterialIcons name="remove-circle" size={28} color="#bbb" />
            <Text style={styles.statsText}>Ngày vắng trong tháng: <Text style={styles.statsNum}>{absent}</Text></Text>
          </View>
        </View>
        <FlatList
          data={records}
          keyExtractor={item => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.label}>Thời gian vào</Text>
              <Text style={styles.value}>{item.timestamp_in}</Text>
              <Text style={styles.label}>Thời gian ra</Text>
              <Text style={styles.value}>{item.timestamp_out || "-"}</Text>
              <Text style={styles.label}>Trạng thái</Text>
              <Text style={[styles.value, item.status === "in" ? styles.in : styles.out]}>{item.status}</Text>
            </View>
          )}
          ListEmptyComponent={<Text style={styles.empty}>Không có dữ liệu điểm danh</Text>}
        />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 30, fontWeight: "bold", marginBottom: 24, color: "#2979ff", textAlign: "center" },
  statsBox: { backgroundColor: "#fff", borderRadius: 16, padding: 18, marginBottom: 22, borderWidth: 1, borderColor: "#e0e0e0", elevation: 3, shadowColor: '#2979ff', shadowOpacity: 0.08, shadowRadius: 8 },
  statsRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  statsText: { fontSize: 18, color: "#2979ff", fontWeight: "bold", marginLeft: 10 },
  statsNum: { color: "#222", fontWeight: "bold", fontSize: 20 },
  card: { backgroundColor: "#fff", borderRadius: 16, padding: 18, marginBottom: 18, borderWidth: 1, borderColor: "#e0e0e0", elevation: 2, shadowColor: '#222', shadowOpacity: 0.07, shadowRadius: 6 },
  label: { fontSize: 16, color: "#2979ff", fontWeight: "bold", marginTop: 6 },
  value: { color: "#222", fontSize: 16, marginBottom: 2 },
  in: { color: "#43a047", fontWeight: "bold" },
  out: { color: "#e53935", fontWeight: "bold" },
  empty: { textAlign: "center", color: "#bbb", fontSize: 16, marginTop: 30 },
});
