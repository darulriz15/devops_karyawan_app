// Jenkinsfile (Versi Final yang Disederhanakan)
pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Mengambil kode dari GitHub...'
                checkout scm
            }
        }

        stage('2. Build & Install Dependencies') {
            steps {
                echo 'Menginstall dependensi Python...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('3. Unit Test') {
            steps {
                echo 'Menjalankan unit tests dengan Pytest...'
                sh 'pytest tests/'
            }
        }

        stage('4. SAST (Static Analysis with Bandit)') {
            steps {
                echo 'Memindai kode dengan Bandit...'
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh 'bandit -r . -ll'
                }
            }
        }

        stage('5. Build Docker Image') {
            steps {
                echo 'Membangun Docker image untuk aplikasi...'
                // Perintah 'sh' sekarang bisa langsung menjalankan 'docker'
                sh 'docker build -t flask-app-staging:${env.BUILD_ID} .'
            }
        }

        stage('6. DAST (Dynamic Analysis with ZAP)') {
            steps {
                script {
                    // Jalankan aplikasi di dalam container untuk di-scan
                    sh 'docker run -d --rm --name dast-target-app -p 8088:5000 flask-app-staging:${env.BUILD_ID}'
                    
                    // Tunggu beberapa detik agar aplikasi benar-benar siap
                    echo 'Menunggu aplikasi siap untuk DAST scan...'
                    sleep 15
                    
                    echo "Memulai OWASP ZAP Scan pada http://127.0.0.1:8088"
                    try {
                        // Jalankan ZAP Scan. Pastikan network-nya bisa menjangkau host
                        sh "docker run --rm --network host -v \$(pwd):/zap/wrk/:rw owasp/zap2docker-stable zap-baseline.py -t http://127.0.0.1:8088 -J zap-report.json"
                    } catch (e) {
                        error "DAST Scan Gagal! Ditemukan kerentanan: ${e.getMessage()}"
                    } finally {
                       // Hentikan container aplikasi setelah scan selesai
                       echo 'Menghentikan container DAST target...'
                       sh 'docker stop dast-target-app'
                       // Publikasikan laporan ZAP sebagai artifact
                       archiveArtifacts artifacts: 'zap-report.json'
                    }
                }
            }
        }

        stage('7. Deploy to Staging') {
            steps {
                echo 'Deployment ke Staging Environment...'
                
                // Hentikan container staging yang lama jika ada
                sh 'docker stop staging-app || true'
                sh 'docker rm staging-app || true'
                
                // Jalankan container baru sebagai staging environment
                sh 'docker run -d --rm --name staging-app -p 5000:5000 flask-app-staging:${env.BUILD_ID}'
                echo 'Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000'
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
