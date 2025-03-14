-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 20, 2025 at 06:10 AM
-- Server version: 10.4.17-MariaDB
-- PHP Version: 8.0.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `form_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'admin', 'pbkdf2:sha256:600000$mHQTCQJSCzzeJl36$26e520aabf34dd0eca9b8c62bee854de916425bf0f25a70d2e181ac0b68c027a');

-- --------------------------------------------------------

--
-- Table structure for table `questions`
--

CREATE TABLE `questions` (
  `id` int(11) NOT NULL,
  `question_text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `questions`
--

INSERT INTO `questions` (`id`, `question_text`) VALUES
(1, '1. Ikaw ba ay nakakaranas ng pananakit o pananakot sa iyong tahanan/bahay?'),
(2, '2. May mga pagkakataon ba na pinag-isipan mong maglayas o umalis na ng inyong bahay?'),
(3, '3. Nakaranas ka ba ng bullying na pisikal o cyber bullying sa paaralan o sa trabaho?'),
(4, '4. May pagkakataon ba na seryoso mong naiisip na wakasan ang iyong buhay?'),
(5, '5. Naninigarilyo ka ba?'),
(6, '6. Umiinom ka ba ng alak?'),
(7, '7. Nakakita ka na ba ng mga ipinagbabawal na \"gamut\" o drugs?'),
(8, '8. Ikaw ba ay nakaranas ng magkarelasyon (boyfriend/girlfriend)?'),
(9, '9. Ikaw ba ay nakaranas ng makipag sex o makipagtalik?'),
(10, '10. Nakaranas ka ba na ikaw ay pinilit makipag sex?'),
(11, '11. Ikaw ba ay nakaranas nang mabuntis, o makabuntis?'),
(12, '12. Gusto mo bang mag pa counsel o komunsulta para matulungan ka?');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `middle_initial` varchar(5) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `dob` date NOT NULL,
  `age` int(11) NOT NULL,
  `sex` varchar(10) NOT NULL,
  `region` varchar(30) NOT NULL,
  `province` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `barangay` varchar(30) NOT NULL,
  `street` varchar(50) NOT NULL,
  `address` varchar(255) NOT NULL,
  `location` text DEFAULT NULL,
  `date` date DEFAULT NULL,
  `submitted_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `first_name`, `middle_initial`, `last_name`, `dob`, `age`, `sex`, `region`, `province`, `city`, `barangay`, `street`, `address`, `location`, `date`, `submitted_at`) VALUES
(1, 'Ruth', 'C', 'Copino', '2002-10-07', 22, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 13:12:39'),
(2, 'Bryan Kim', 'D.', 'Manlapaz', '2003-01-01', 22, 'Male', '', '', '', '', '', '', 'Health Center', '2025-02-18', '2025-02-18 13:18:05'),
(3, 'Cindy', 'C.', 'Ceron', '2001-01-01', 24, 'Female', '', '', '', '', '', '', 'Health Center', '2025-02-18', '2025-02-18 13:28:19'),
(4, 'Maeven', 'S.', 'Armada', '2003-01-01', 22, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 13:39:19'),
(5, 'Maeven', 'S.', 'Armada', '2003-01-01', 22, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 13:40:47'),
(6, 'Rochel', 'C.', 'Copino', '1996-12-10', 28, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 13:59:05'),
(7, 'Ann', 'C. ', 'Copino', '1998-08-07', 26, 'Female', '', '', '', '', '', '', 'Health Center', '2025-02-18', '2025-02-18 14:06:53'),
(8, 'Kyla', 'S. ', 'Verona', '2003-01-01', 22, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 14:14:37'),
(9, 'Ruthy', 'C.', 'Copino', '2010-10-07', 14, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 14:19:24'),
(10, 'Ruthyy', 'C.', 'Copino', '2010-02-01', 15, 'Female', '', '', '', '', '', '', 'School', '2025-02-18', '2025-02-18 14:22:55'),
(11, 'Bryan Kim', 'D.', 'Manlapaz', '2003-05-10', 21, 'Male', '', '', '', '', '', '', 'Other', '2025-02-19', '2025-02-19 00:32:39'),
(12, 'Ruth', 'D.', 'Copino', '2019-06-19', 5, 'Female', '', '', '', '', '', '', NULL, '2025-02-19', '2025-02-19 01:37:53'),
(13, 'Ruth', 'D.', 'Copino', '2003-05-10', 21, 'Female', '', '', '', '', '', '', 'School', '2025-02-20', '2025-02-20 00:40:01'),
(14, 'Ruth', 'D.', 'Copino', '2003-05-10', 21, 'Female', '', '', '', '', '', '', 'School', '2025-02-20', '2025-02-20 00:42:30'),
(15, 'Ruth', 'C.', 'Copino', '2018-06-06', 6, 'Female', '', '', '', '', '', '', 'School', '2025-02-20', '2025-02-20 00:43:07'),
(16, 'Bryan Kim', 'D.', 'Manlapaz', '2003-05-10', 21, 'Male', '08', '0837', '083702', '083702035', '', '', 'School', '2025-02-20', '2025-02-20 03:27:55');

-- --------------------------------------------------------

--
-- Table structure for table `user_response`
--

CREATE TABLE `user_response` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `question_number` int(11) NOT NULL,
  `response` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user_response`
--

INSERT INTO `user_response` (`id`, `user_id`, `question_number`, `response`) VALUES
(1, 1, 1, 'No'),
(2, 0, 1, 'No'),
(3, 0, 1, 'Yes'),
(4, 519, 1, 'Yes'),
(5, 519, 2, 'Yes'),
(6, 7, 3, 'Yes'),
(7, 7, 4, 'Yes'),
(8, 7, 4, 'Yes'),
(9, 7, 5, 'No'),
(10, 7, 6, 'No'),
(11, 7, 7, 'Yes'),
(12, 7, 8, 'No'),
(13, 7, 9, 'No'),
(14, 7, 10, 'No'),
(15, 7, 11, 'No'),
(16, 7, 12, 'No'),
(17, 8, 1, 'Yes'),
(18, 8, 2, 'No'),
(19, 8, 3, 'No'),
(20, 8, 4, 'No'),
(21, 8, 5, 'No'),
(22, 8, 6, 'Yes'),
(23, 8, 7, 'Yes'),
(24, 8, 8, 'No'),
(25, 8, 9, 'No'),
(26, 8, 10, 'No'),
(27, 8, 11, 'No'),
(28, 8, 12, 'No'),
(29, 10, 1, 'Yes'),
(30, 10, 2, 'Yes'),
(31, 10, 3, 'No'),
(32, 10, 4, 'No'),
(33, 10, 5, 'No'),
(34, 10, 6, 'Yes'),
(35, 10, 7, 'No'),
(36, 10, 8, 'Yes'),
(37, 10, 9, 'No'),
(38, 10, 10, 'No'),
(39, 10, 11, 'No'),
(40, 10, 12, 'No'),
(41, 10, 12, 'No'),
(42, 0, 1, 'No'),
(43, 11, 1, 'No'),
(44, 11, 2, 'Yes'),
(45, 11, 3, 'Yes'),
(46, 11, 4, 'No'),
(47, 11, 5, 'No'),
(48, 11, 6, 'No'),
(49, 11, 7, 'No'),
(50, 11, 8, 'Yes'),
(51, 11, 9, 'No'),
(52, 11, 10, 'No'),
(53, 11, 11, 'No'),
(54, 11, 12, 'Yes'),
(55, 15, 1, 'Yes'),
(56, 15, 2, 'No'),
(57, 15, 2, 'Yes');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user_response`
--
ALTER TABLE `user_response`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `questions`
--
ALTER TABLE `questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `user_response`
--
ALTER TABLE `user_response`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
