// Jenkinsfile FINAL (dengan perbaikan docker: not found)
pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            // Menjalankan sebagai root agar bisa install paket & menjalankan docker
            args '-v /var/run/docker.sock:/var/run/docker.sock --user root'
        }
    }
    environment {
        APP_USER = 'admin'
        APP_PASSWORD = 'password123'
    }
    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Mengambil kode dari GitHub...'
                checkout scm
            }
        }
        // TAHAP BARU UNTUK MENGINSTALL DOCKER CLIENT
        stage('2. Setup Environment') {
            steps {
                echo 'Installing Docker client inside the agent...'
                sh 'apt-get update && apt-get install -y docker.io'
            }
        }
        stage('3. Build & Install Dependencies') {
            steps {
                echo 'Menginstall dependensi Python...'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('4. Unit Test') {
            steps {
                echo 'Menjalankan unit tests dengan Pytest...'
                sh 'PYTHONPATH=. pytest tests/'
            }
        }
	// Jenkinsfile - Modifikasi Stage 5
	stage('5. SAST (Static Analysis with Bandit)') {
	    steps {
	        echo 'Memindai kode untuk kerentanan HIGH...'
	        // -lll : Hanya laporkan isu level HIGH
	        // Jika ada temuan, exit code akan != 0 dan akan menggagalkan pipeline
	        sh 'bandit -r . -lll'
	    }
	}
        stage('6. Build Docker Image') {
            steps {
                echo 'Membangun Docker image untuk aplikasi...'
                sh "docker build -t flask-app-staging:${env.BUILD_ID} ."
            }
        }
	// Jenkinsfile - Ganti Stage 7 dengan ini
	stage('7. DAST (Dynamic Analysis with ZAP)') {
	    steps {
	        script {
	            sh "docker run -d --rm --name dast-target-app -p 8088:5000 flask-app-staging:${env.BUILD_ID}"
	            echo 'Menunggu 15 detik agar aplikasi siap...'
	            sleep 15

	            def zapReportJson = ''
	            try {
	                echo "Memulai ZAP Scan dan menangkap output JSON..."
	                // Jalankan ZAP untuk mencetak JSON ke stdout (-j) dan paksa selalu sukses (|| true)
	                // agar kita bisa selalu menangkap laporannya untuk dianalisis.
	                zapReportJson = sh(
	                    script: "docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://127.0.0.1:8088 -T 5 -j || true",
	                    returnStdout: true
	                ).trim()

	                // Tulis output yang ditangkap ke dalam file
	                writeFile file: 'zap-report.json', text: zapReportJson
	                archiveArtifacts artifacts: 'zap-report.json', allowEmptyArchive: true

	                // === BAGIAN LOGIKA BARU UNTUK CEK HASIL ===
	                if (zapReportJson) {
	                    def report = readJSON text: zapReportJson
	                    // ZAP menggunakan riskcode '3' untuk 'High'
	                    def highAlerts = report.site.alerts.findAll { it.riskcode == '3' }

	                    if (highAlerts.size() > 0) {
	                        // GAGALKAN BUILD JIKA DITEMUKAN KERENTANAN 'HIGH'
	                        error "DAST GAGAL: Ditemukan ${highAlerts.size()} kerentanan dengan tingkat HIGH."
	                    } else {
	                        echo "DAST Selesai: Tidak ditemukan kerentanan tingkat HIGH."
	                    }
	                } else {
	                    echo "Peringatan: Laporan ZAP tidak berhasil ditangkap."
	                }

	            } finally {
	                echo 'Menghentikan container DAST target...'
	                sh 'docker stop dast-target-app || true'
	            }
	        }
	    }
	}
        stage('8. Deploy to Staging') {
            steps {
                echo 'Deployment ke Staging Environment...'
                sh 'docker stop staging-app || true'
                sh 'docker rm staging-app || true'
                sh "docker run -d --rm --name staging-app -p 5000:5000 flask-app-staging:${env.BUILD_ID}"
                echo "Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000"
            }
        }
    }
    post {
        always {
            echo 'Membersihkan workspace...'
            cleanWs()
        }
    }
}
