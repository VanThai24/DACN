import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons, MaterialIcons, FontAwesome5 } from '@expo/vector-icons';

export default function BottomTabBar({ state, descriptors, navigation }) {
  return (
    <View style={styles.tabBar}>
      <TouchableOpacity style={styles.tab} onPress={() => navigation.navigate('Home')}>
        <Ionicons name="home-outline" size={28} color={state.index === 0 ? '#2979ff' : '#bbb'} />
        <Text style={[styles.label, state.index === 0 && styles.activeLabel]}>Trang chủ</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.tab} onPress={() => navigation.navigate('Attendance')}>
        <MaterialIcons name="event-note" size={26} color={state.index === 1 ? '#2979ff' : '#bbb'} />
        <Text style={[styles.label, state.index === 1 && styles.activeLabel]}>Điểm danh</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.tab} onPress={() => navigation.navigate('Profile')}>
        <FontAwesome5 name="user-alt" size={24} color={state.index === 2 ? '#2979ff' : '#bbb'} />
        <Text style={[styles.label, state.index === 2 && styles.activeLabel]}>Cá nhân</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    height: 64,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderColor: '#eee',
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  label: {
    fontSize: 13,
    color: '#bbb',
    marginTop: 2,
  },
  activeLabel: {
    color: '#2979ff',
    fontWeight: 'bold',
  },
});
