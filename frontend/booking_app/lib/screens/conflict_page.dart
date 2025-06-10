import 'package:flutter/material.dart';
import '../models/reservation.dart';
import '../services/api_service.dart';

class ConflictPage extends StatefulWidget {
  const ConflictPage({super.key});

  @override
  State<ConflictPage> createState() => _ConflictPageState();
}

class _ConflictPageState extends State<ConflictPage> {
  late Future<List<Reservation>> _pendingReservations;

  @override
  void initState() {
    super.initState();
    _pendingReservations = ApiService.fetchPendingConflicts();
  }

  void _refreshList() {
    setState(() {
      _pendingReservations = ApiService.fetchPendingConflicts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("⛔ 拒否確認待ち予約")),
      body: FutureBuilder<List<Reservation>>(
        future: _pendingReservations,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text("エラー: ${snapshot.error}"));
          }

          final reservations = snapshot.data!;
          if (reservations.isEmpty) {
            return const Center(child: Text("現在、確認待ちの予約はありません 🙌"));
          }

          return ListView.builder(
            itemCount: reservations.length,
            itemBuilder: (context, index) {
              final r = reservations[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                elevation: 3,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("📌 目的: ${r.purpose}", style: const TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text("🕒 ${r.startTime} ～ ${r.endTime}"),
                      Text("🖥️ サーバー: ${r.serverName ?? '（未設定）'}"),
                      Text("🔥 優先度: ${r.priorityScore?.toStringAsFixed(2) ?? 'N/A'}"),
                      Text("📌 ステータス: ${r.status}"),
                      const SizedBox(height: 8),
                      Align(
                        alignment: Alignment.centerRight,
                        child: ElevatedButton(
                          onPressed: () async {
                            await ApiService.confirmCancelReservation(r.id.toString());
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text("予約を承諾（拒否）しました")),
                            );
                            _refreshList(); // 更新
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.redAccent,
                          ),
                          child: const Text("承諾", style: TextStyle(color: Colors.white)),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
