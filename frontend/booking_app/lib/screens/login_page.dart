import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  String message = "";

Future<void> login() async {
  final url = Uri.parse('${dotenv.env['AWS_API_URL']}');
  final body = {
    'action': 'login',
    'username': usernameController.text,
    'password': passwordController.text,
  };

  print("📡 POST to: $url");
  print("📦 body: ${jsonEncode(body)}");

  try {
    final response = await http
        .post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 10), onTimeout: () {
          throw Exception("⏱ タイムアウトしました");
        });

    print("🛰 statusCode: ${response.statusCode}");
    print("📨 response: ${response.body}");

    if (response.statusCode == 200) {
      final jsonResponse = jsonDecode(response.body);
      final token = jsonResponse['token'];

      if (token != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('token', token);

        setState(() {
          message = "✅ ログイン成功！";
        });

        Navigator.pushReplacementNamed(context, '/booking');
      } else {
        setState(() {
          message = "⚠️ トークンが受け取れませんでした";
        });
      }
    } else {
      String errorMessage = "❌ ログイン失敗 (${response.statusCode})";

      try {
        final bodyJson = jsonDecode(response.body);
        if (bodyJson['error'] != null) {
          errorMessage += "\n${bodyJson['error']}";
        }
      } catch (e) {
        // 念のためエラーがJSONでない時も無視
      }

      setState(() {
        message = errorMessage;
      });
    }

  } catch (e) {
    print("❌ 通信エラー: $e");
    setState(() {
      message = "❌ 通信エラー";
    });
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("ログイン")),
      body: SafeArea(
        child: GestureDetector(
          onTap: () => FocusScope.of(context).unfocus(), // タップでキーボード閉じる
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: MediaQuery.of(context).size.height - kToolbarHeight - MediaQuery.of(context).padding.top,
              ),
              child: IntrinsicHeight(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextField(
                      controller: usernameController,
                      decoration: const InputDecoration(labelText: "ユーザー名"),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: passwordController,
                      decoration: const InputDecoration(labelText: "パスワード"),
                      obscureText: true,
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: login,
                      child: const Text("ログイン"),
                    ),
                    const SizedBox(height: 12), // ← ここで余白調整
                    TextButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/register');
                      },
                      child: const Text("▶ 新規登録はこちら", style: TextStyle(fontSize: 16)),
                    ),
                    const SizedBox(height: 16),
                    Text(message),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}


