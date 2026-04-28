def get_response(user_input):
    user_input = user_input.lower()

    if any(word in user_input for word in ["hi", "hello", "hey"]):
        return "👋 Hello! I am EduQuery AI 🤖. How can I assist you today?"

    elif "exam" in user_input:
        return "📚 Exams are usually conducted in May/December. Please check CUIMS portal."

    # ✅ SMART FEE LOGIC (MULTIPLE COURSES)
    elif "fee" in user_input:

        if "mca" in user_input:
            return "💰 MCA fee is approximately ₹1.2–1.5 lakh per year."

        elif "btech" in user_input or "b.tech" in user_input:
            return "💰 B.Tech fee is approximately ₹2–2.5 lakh per year."

        elif "mba" in user_input:
            return "💰 MBA fee is approximately ₹3–4 lakh per year."

        elif "bba" in user_input:
            return "💰 BBA fee is approximately ₹1–1.5 lakh per year."

        else:
            return "💰 Please select a course (MCA, B.Tech, MBA, BBA) to get exact fee details."

    elif "admission" in user_input:
        return "🎓 Admissions are open. You can apply through the Chandigarh University official website."

    elif "course" in user_input:
        return "📖 CU offers B.Tech, MBA, MCA, BBA and many more programs."

    elif "placement" in user_input:
        return "💼 CU has strong placements with companies like Amazon, Microsoft, Infosys."

    elif "hostel" in user_input:
        return "🏠 Hostel facilities are available with modern amenities and security."

    elif "library" in user_input:
        return "📚 Library is open from 9 AM to 8 PM with digital access."

    elif "timing" in user_input:
        return "⏰ College timings are usually 9 AM to 5 PM."

    # ✅ CLEAN FALLBACK
    else:
        return """🤖 I’m still learning and may not have the exact answer for this.

For further assistance, you can connect with our Student Support Team.

👉 Would you like to request a callback from our support team?"""