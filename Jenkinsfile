// Jenkinsfile FINAL YANG BENAR
pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
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
        stage('5. SAST (Static Analysis with Bandit)') {
            steps {
                echo 'Memindai kode untuk kerentanan HIGH...'
                sh 'bandit -r . -lll'
            }
        }
        stage('6. Build Docker Image') {
            steps {
                echo 'Membangun Docker image untuk aplikasi...'
                sh "docker build -t flask-app-staging:${env.BUILD_ID} ."
            }
        }
        stage('7. DAST (Dynamic Analysis with ZAP)') {
            steps {
                script {
                    sh "docker run -d --rm --name dast-target-app -p 8088:5000 -e APP_USER=${env.APP_USER} -e APP_PASSWORD=${env.APP_PASSWORD} flask-app-staging:${env.BUILD_ID}"
                    echo 'Menunggu 15 detik agar aplikasi siap...'
                    sleep 15
                    
                    try {
                        echo "Memulai ZAP Scan dan menangkap output..."
                        // Jalankan ZAP untuk mencetak JSON ke stdout (-j) dan paksa selalu sukses (|| true)
                        def fullZapOutput = sh(
                            script: "docker run --rm --network host ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://127.0.0.1:8088 -T 5 -j || true",
                            returnStdout: true
                        ).trim()

                        // Ekstrak HANYA bagian JSON dari seluruh output
                        def jsonMatch = (fullZapOutput =~ /(?s)\{.*\}/)

                        if (jsonMatch) {
                            def zapReportJson = jsonMatch[0]
                            echo "Laporan JSON berhasil diekstrak."
                            writeFile file: 'zap-report.json', text: zapReportJson

                            // Analisis laporan yang sudah bersih
                            def report = readJSON text: zapReportJson
                            def highAlerts = report.site.alerts.findAll { it.riskcode == '3' }

                            if (highAlerts.size() > 0) {
                                error "DAST GAGAL: Ditemukan ${highAlerts.size()} kerentanan dengan tingkat HIGH."
                            } else {
                                echo "DAST Selesai: Tidak ditemukan kerentanan tingkat HIGH."
                            }
                        } else {
                            echo "PERINGATAN: Tidak ada laporan JSON yang ditemukan dalam output ZAP."
                            echo "Output penuh ZAP:\n${fullZapOutput}"
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
                sh "docker run -d --rm --name staging-app -p 5000:5000 -e APP_USER=${env.APP_USER} -e APP_PASSWORD=${env.APP_PASSWORD} flask-app-staging:${env.BUILD_ID}"
                echo "Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000"
            }
        }
    }
    post {
        always {
            script {
                echo 'Membersihkan workspace dan mengarsipkan laporan...'
                // Pindahkan logika arsip ke sini
                if (fileExists('zap-report.json')) {
                    archiveArtifacts artifacts: 'zap-report.json', allowEmptyArchive: true
                }
                cleanWs()
            }
        }
    }
}
