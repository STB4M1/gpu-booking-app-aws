class Reservation {
  final String id; // ← ここを String に変更！
  final DateTime startTime;
  final DateTime endTime;
  final String purpose;
  final String status;
  final double priorityScore;
  final String? serverName;

  Reservation({
    required this.id,
    required this.startTime,
    required this.endTime,
    required this.purpose,
    required this.status,
    required this.priorityScore,
    this.serverName,
  });

  factory Reservation.fromJson(Map<String, dynamic> json) {
    return Reservation(
      id: json['id'], // ← これも String 扱いでOK
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      purpose: json['purpose'],
      status: json['status'],
      priorityScore: double.parse(json['priority_score'].toString()),
      serverName: json['server_name'],
    );
  }
}
