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
                    // Jalankan container aplikasi dengan Environment Variables
                    sh "docker run -d --rm --name dast-target-app -p 8088:5000 -e APP_USER=${env.APP_USER} -e APP_PASSWORD=${env.APP_PASSWORD} flask-app-staging:${env.BUILD_ID}"
                    echo 'Menunggu 15 detik agar aplikasi siap...'
                    sleep 15

                    try {
                        echo "Memulai OWASP ZAP Scan..."
                        // Jalankan ZAP sebagai root dan biarkan ia menulis laporan
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "docker run --rm --network host --user root -v ${pwd()}:/zap/wrk/:rw ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://127.0.0.1:8088 -J zap-report.json -l FAIL"
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
                // Jalankan container aplikasi dengan Environment Variables
                sh "docker run -d --rm --name staging-app -p 5000:5000 -e APP_USER=${env.APP_USER} -e APP_PASSWORD=${env.APP_PASSWORD} flask-app-staging:${env.BUILD_ID}"
                echo "Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000"
            }
        }
    }
    post {
        always {
            // Arsipkan laporan HANYA jika file-nya ada
            script {
                if (fileExists('zap-report.json')) {
                    archiveArtifacts artifacts: 'zap-report.json'
                }
                cleanWs()
            }
        }
    }
}
