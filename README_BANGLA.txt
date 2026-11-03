সরাসরি Windows EXE বানানোর ক্লাউড বিল্ড প্যাকেজ

এই প্যাকেজটি Windows EXE নিজে থেকে তৈরি করে না। GitHub-এর Windows কম্পিউটারে
বিল্ড চালিয়ে NetworkMonitor.exe তৈরি করে দেবে। আপনার নিজের PC-তে Python লাগবে না।

ধাপ:
1. github.com এ সাইন ইন করুন (ফ্রি অ্যাকাউন্ট চলবে)।
2. New repository তৈরি করুন, নাম দিন NetworkMonitor এবং Public বা Private রাখুন।
3. এই ZIP Extract করে ভেতরের সব ফাইল/ফোল্ডার repository-তে Upload files দিয়ে আপলোড ও Commit করুন।
   .github ফোল্ডারটিও আপলোড করতে হবে।
4. Repository-তে Actions ট্যাব খুলুন।
5. বাম পাশে "Build Windows EXE" নির্বাচন করে "Run workflow" চাপুন।
6. বিল্ড শেষ হলে নিচের Artifacts থেকে NetworkMonitor-Windows.zip ডাউনলোড করুন।
7. ZIP Extract করলে NetworkMonitor.exe পাবেন।

EXE চালাতে Python ইনস্টল লাগবে না।
Windows SmartScreen সতর্কতা দেখালে অজানা উৎসের EXE চালানোর আগে ফাইলটি যাচাই করুন।
