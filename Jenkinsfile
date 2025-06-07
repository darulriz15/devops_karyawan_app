// Jenkinsfile (Sudah diperbaiki)
pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            // Argumen ini penting agar container agent ini bisa mengontrol Docker di host
            // untuk menjalankan stage DAST dan Deploy
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo 'Mencari dan mengambil kode dari GitHub...'
                checkout scm
            }
        }

        stage('2. Build & Install Dependencies') {
            steps {
                echo 'Mempersiapkan environment dan menginstall dependensi Python...'
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
                echo 'Memindai kode untuk kerentanan dengan Bandit...'
                catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                    sh 'bandit -r . -ll'
                }
            }
        }

        stage('5. DAST (Dynamic Analysis with ZAP)') {
            steps {
                script {
                    echo 'Membangun Docker image untuk aplikasi...'
                    // Kita perlu menggunakan 'docker.Image.inside' untuk menjalankan perintah docker dari dalam docker agent
                    docker.image('python:3.9-slim').inside('-v /var/run/docker.sock:/var/run/docker.sock') {
                        def dockerImage = docker.build("flask-app-staging:${env.BUILD_ID}")

                        dockerImage.withRun("--name dast-target-app") { c ->
                            echo "Aplikasi sementara berjalan di container ${c.id}"
                            sleep 10
                            
                            echo "Memulai OWASP ZAP Scan..."
                            try {
                                sh "docker run --rm --network host -v \$(pwd):/zap/wrk/:rw owasp/zap2docker-stable zap-baseline.py -t http://127.0.0.1:8080 -J zap-report.json"
                            } catch (e) {
                                error "DAST Scan Gagal! Ditemukan kerentanan: ${e.getMessage()}"
                            } finally {
                               archiveArtifacts artifacts: 'zap-report.json'
                            }
                        }
                    }
                }
            }
        }


        stage('6. Deploy to Staging') {
            steps {
                script {
                    echo 'Deployment ke Staging Environment...'
                    // Menggunakan teknik yang sama seperti DAST
                    docker.image('python:3.9-slim').inside('-v /var/run/docker.sock:/var/run/docker.sock') {
                        def dockerImage = docker.build("flask-app-staging:${env.BUILD_ID}")
                        
                        sh 'docker stop staging-app || true'
                        sh 'docker rm staging-app || true'
                        
                        dockerImage.run("--name staging-app -p 5000:5000")
                        echo 'Aplikasi berhasil di-deploy ke http://<IP_KALI_LINUX_ANDA>:5000'
                    }
                }
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
