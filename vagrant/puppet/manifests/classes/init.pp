class init {
    exec { "apt-update":
        command => "/usr/bin/apt-get update",
        timeout => 0,
    }

    Exec["apt-update"] -> Package <| |>

    class { 'postgresql::globals':
      encoding => 'UTF-8',
      locale   => 'en_US.UTF-8',
    }->
    class { 'postgresql::server': }

    postgresql::server::db { 'crawldemo':
      user     => 'crawldemo',
      password => postgresql_password('crawldemo', 'crawldemo'),
    }

    package {
        ['build-essential', 'python', 'python-dev', 'python-virtualenv', 'libevent-dev', 'libpq-dev', 'libmemcached-dev', 'zlib1g-dev', 'libssl-dev', 'python-pip', 'libjpeg-dev']:
        ensure => 'installed',
        require => Exec['apt-update'] # The system update needs to run first
    }
}
