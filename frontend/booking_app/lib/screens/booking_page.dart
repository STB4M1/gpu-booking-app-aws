import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'reservation_list_page.dart';
import 'conflict_page.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/reservation.dart';

class BookingPage extends StatefulWidget {
  const BookingPage({super.key});

  @override
  State<BookingPage> createState() => _BookingPageState();
}

class _BookingPageState extends State<BookingPage> {
  final TextEditingController _controller = TextEditingController();
  String _result = "";

Future<void> sendText() async {
  final text = _controller.text;
  print("📤 入力文を送信します: $text");

  try {
    final dynamic data = await ApiService.sendNaturalText(text);

    if (data is Reservation) {
      // ✅ 正常に構造化＆予約成功
      setState(() {
        _result = '''
✅ 通信成功！

🕒 開始: ${data.startTime}  
🕕 終了: ${data.endTime}  
🎯 目的: ${data.purpose}  
📌 ステータス: ${data.status}  
🔥 優先度: ${data.priorityScore}
🖥️ サーバー名: ${data.serverName} 
''';
      });
    } else if (data is Map<String, dynamic> && data['missing_fields'] != null) {
      // ⚠️ 構造化成功したが情報不足
      final missing = data['missing_fields'].join("、");

      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text("情報が不足しています"),
          content: Text("以下の情報が足りません：\n\n$missing"),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("OK"),
            ),
          ],
        ),
      );
    } else {
      // ❌ 想定外のレスポンス
      setState(() {
        _result = "❌ 不明なエラーが発生しました。";
      });
    }

  } catch (e) {
    // 例外が出た場合（API通信失敗など）
    setState(() {
      _result = "❌ 通信エラー: ${e.toString().replaceFirst('Exception: ', '')}";
    });
  }
}


  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token'); // ✅ トークン削除
    Navigator.pushReplacementNamed(context, '/'); // ✅ ログイン画面へ戻る
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
        title: const Text("GPU予約アプリ"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'ログアウト',
            onPressed: logout,
          ),
        ],
      ),
      body: SafeArea(
        child: GestureDetector(
          // 🧼 タップでキーボード閉じる
          onTap: () => FocusScope.of(context).unfocus(),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: _controller,
                  decoration: const InputDecoration(
                    labelText: "自然文で予約希望を入力してください",
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                  keyboardType: TextInputType.multiline,
                ),
                RichText(
                  text: TextSpan(
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                    children: [
                      TextSpan(
                        text: '\n📋 必要事項:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextSpan(
                        text:
                            ' 日付・開始時間・終了時間（または使用時間）・目的・サーバー名',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: sendText,
                  child: const Text("予約リクエスト送信"),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ReservationListPage()),
                    );
                  },
                  child: const Text("予約一覧を表示"),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ConflictPage()),
                    );
                  },
                  child: const Text("拒否確認待ち一覧を表示"),
                ),

                const SizedBox(height: 16),
                Text(
                  _result,
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

